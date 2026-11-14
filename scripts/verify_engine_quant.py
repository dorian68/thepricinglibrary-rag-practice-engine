"""Quant-grade verification harness for the deterministic pricing engines.

This is the *judge* of the self-checking loop. It re-derives every number the
engines emit with an INDEPENDENT reference implementation and asserts equality,
then runs conceptual checks a quant/trader would insist on:

  - Black-Scholes call price, delta, gamma, vega vs closed form.
  - European PUT via the engine must satisfy call-put parity exactly.
  - Greeks P&L attribution with correct units (per-1% sensitivities).
  - Swap PV / DV01 sign and magnitude.
  - Canonical fixed-rate bond schedule, clean/dirty/accrued, YTM inversion,
    duration/convexity and exact/cash-flow-attributed DV01, plus the historical
    duration-only practice proxy.
  - FX barrier conditional payoff.
  - CDS: ANNUAL premium (spread*notional) must NOT be conflated with the
    PV of the premium leg (spread*risky_annuity*notional).
  - Parametric VaR must use the EXACT inverse-normal quantile for the requested
    confidence (not a binary 1.65/2.33 cutoff), and ship an Expected Shortfall.

Run offline (no LLM, no network):
    python scripts/verify_engine_quant.py
Exit code 0 = all terminal conditions met. Non-zero = a defect remains.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pricinglibrary_rag import course_blocks as cb
from pricinglibrary_rag.calculators import PracticeCalculator
from pricinglibrary_rag.bond import analyze_bond
from pricinglibrary_rag.black_scholes import BLACK_SCHOLES_INPUT_SCHEMA, analyze_black_scholes
from pricinglibrary_rag.realized_volatility import analyze_realized_volatility
from pricinglibrary_rag.vol_surface import INPUT_SCHEMA as VOL_SURFACE_INPUT_SCHEMA, analyze_vol_surface
from pricinglibrary_rag.yield_curve import build_yield_curve

TOL = 1e-6
FAILURES: list[str] = []
CHECKS = 0
YIELD_CURVE_FIXTURE_PATH = (
    Path(__file__).resolve().parents[3] / "fixtures" / "yield_curve_golden.json"
)
REALIZED_VOLATILITY_FIXTURE_PATH = (
    Path(__file__).resolve().parents[3]
    / "fixtures"
    / "realized_volatility_golden.json"
)


def check(name: str, got: float, ref: float, tol: float = TOL) -> None:
    global CHECKS
    CHECKS += 1
    if ref == 0:
        ok = abs(got) <= tol
    else:
        ok = abs(got - ref) <= tol * max(1.0, abs(ref))
    status = "ok " if ok else "FAIL"
    print(f"  [{status}] {name}: got={got:.6g} ref={ref:.6g}")
    if not ok:
        FAILURES.append(f"{name}: got={got!r} ref={ref!r}")


def check_true(name: str, cond: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    status = "ok " if cond else "FAIL"
    print(f"  [{status}] {name}{(' - ' + detail) if detail else ''}")
    if not cond:
        FAILURES.append(f"{name}: {detail}")


# --- independent reference math -------------------------------------------

def n_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def n_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def n_inv(p: float) -> float:
    """Acklam inverse normal CDF (independent of engine implementation)."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def bs(S, K, sigma, T, r, q=0.0):
    d1 = (math.log(S/K) + (r - q + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))
    d2 = d1 - sigma*math.sqrt(T)
    call = S*math.exp(-q*T)*n_cdf(d1) - K*math.exp(-r*T)*n_cdf(d2)
    put = K*math.exp(-r*T)*n_cdf(-d2) - S*math.exp(-q*T)*n_cdf(-d1)
    delta = math.exp(-q*T)*n_cdf(d1)
    gamma = math.exp(-q*T)*n_pdf(d1)/(S*sigma*math.sqrt(T))
    vega_pt = S*math.exp(-q*T)*n_pdf(d1)*math.sqrt(T)/100
    return dict(d1=d1, d2=d2, call=call, put=put, delta=delta, gamma=gamma, vega_pt=vega_pt)


def step_result(pack, label_contains: str) -> str:
    for s in pack.steps:
        if label_contains.lower() in s.label.lower():
            return s.result
    return ""


def num(text: str) -> float:
    """Pull the first signed number out of an engine result string."""
    import re
    m = re.search(r"[-+]?\d[\d,\s]*\.?\d*", text.replace(" ", ""))
    if not m:
        return float("nan")
    return float(m.group(0).replace(",", "").replace(" ", ""))


def curve_node_at(result: dict, time: float) -> dict | None:
    return next(
        (
            node
            for node in result["curve"]
            if abs(float(node["time"]) - time) <= 1e-12
        ),
        None,
    )


def curve_discount_at(result: dict, time: float) -> float:
    if abs(time) <= 1e-12:
        return 1.0
    node = curve_node_at(result, time)
    return float("nan") if node is None else float(node["discountFactor"])


def realized_volatility_reference(rows: list[dict], annualization: int) -> dict:
    """Independent five-estimator reference using only the published formulas."""
    close_returns: list[float] = []
    overnight_returns: list[float] = []
    intraday_returns: list[float] = []
    parkinson_terms: list[float] = []
    garman_klass_terms: list[float] = []
    rogers_satchell_terms: list[float] = []
    for index in range(1, len(rows)):
        previous_close = float(rows[index - 1]["close"])
        row = rows[index]
        open_price = float(row["open"])
        high = float(row["high"])
        low = float(row["low"])
        close = float(row["close"])
        close_return = math.log(close / previous_close)
        overnight = math.log(open_price / previous_close)
        intraday = math.log(close / open_price)
        log_range = math.log(high / low)
        close_returns.append(close_return)
        overnight_returns.append(overnight)
        intraday_returns.append(intraday)
        parkinson_terms.append(log_range**2 / (4 * math.log(2)))
        garman_klass_terms.append(
            0.5 * log_range**2
            - (2 * math.log(2) - 1) * intraday**2
        )
        rogers_satchell_terms.append(
            math.log(high / close) * math.log(high / open_price)
            + math.log(low / close) * math.log(low / open_price)
        )
    count = len(close_returns)

    def sample_variance(values: list[float]) -> float:
        mean = math.fsum(values) / len(values)
        return math.fsum((value - mean) ** 2 for value in values) / (len(values) - 1)

    k = 0.34 / (1.34 + (count + 1) / (count - 1))
    variances = {
        "closeToClose": sample_variance(close_returns),
        "parkinson": math.fsum(parkinson_terms) / count,
        "garmanKlass": math.fsum(garman_klass_terms) / count,
        "rogersSatchell": math.fsum(rogers_satchell_terms) / count,
    }
    variances["yangZhang"] = (
        sample_variance(overnight_returns)
        + k * sample_variance(intraday_returns)
        + (1 - k) * variances["rogersSatchell"]
    )
    variances = {
        name: 0.0 if -1e-15 <= value < 0 else value
        for name, value in variances.items()
    }
    return {
        "n": count,
        "k": k,
        "variances": variances,
        "annualized": {
            name: math.sqrt(annualization * value)
            for name, value in variances.items()
        },
    }


calc = PracticeCalculator()

print("="*72)
print("1. BLACK-SCHOLES (call, delta, gamma, vega) + PUT via parity")
ref = bs(100, 100, 0.20, 1.0, 0.05)
pack = calc.build_pack(cb.seed_for_topic("vanilla_bs")[1], family_hint="vanilla_option_black_scholes")
check("BS call", num(step_result(pack, "Prix call")), ref["call"], tol=1e-3)
greeks = step_result(pack, "Greeks")
import re as _re
m = {k: float(v) for k, v in _re.findall(r"(Delta|Gamma|Vega/vol pt)=([-\d.]+)", greeks)}
check("BS delta", m.get("Delta", float("nan")), ref["delta"], tol=1e-3)
check("BS gamma", m.get("Gamma", float("nan")), ref["gamma"], tol=1e-4)
check("BS vega/pt", m.get("Vega/vol pt", float("nan")), ref["vega_pt"], tol=1e-3)
put_str = step_result(pack, "put")
check_true("BS worked example ships a PUT price", bool(put_str), "no put step found")
if put_str:
    check("BS put (via engine)", num(put_str), ref["put"], tol=1e-2)
    # parity: C - P == S - K e^{-rT}
    parity_rhs = 100 - 100*math.exp(-0.05*1.0)
    check("Call-put parity C-P", ref["call"] - num(put_str), parity_rhs, tol=1e-2)

print("="*72)
print("2. OPTIONS BOOK GREEKS P&L (units: per-1% sensitivities)")
pack = calc.build_pack(cb.seed_for_topic("greeks")[1], family_hint="options_book_greeks")
# delta +250k/1%, gamma -80k/1%^2, vega +120k/pt, theta -15k/d; spot -2%, vol +3
check("greeks delta P&L", num(step_result(pack, "P&L delta")), 250000*(-2))
check("greeks gamma P&L", num(step_result(pack, "P&L gamma")), 0.5*(-80000)*(-2)**2)
check("greeks vega P&L", num(step_result(pack, "P&L vega")), 120000*3)
check("greeks theta P&L", num(step_result(pack, "P&L theta")), -15000.0)
check("greeks total P&L", num(step_result(pack, "total")), -500000-160000+360000-15000)

print("="*72)
print("3. RATES SWAP PV / DV01 (payer)")
pack = calc.build_pack(cb.seed_for_topic("swap")[1], family_hint="rates_swap_dv01")
check("swap DV01", num(step_result(pack, "DV01")), 4.55*100e6*0.0001)
check("swap PV payer", num(step_result(pack, "PV payer")), (3.0/100-3.2/100)*4.55*100e6)
check("swap shock P&L", num(step_result(pack, "shock")), 4.55*100e6*0.0001*10)

print("="*72)
print("4. BOND: canonical schedule/quote/risk + historical practice proxy")
pack = calc.build_pack(cb.seed_for_topic("bond")[1], family_hint="bond_duration_dv01")
check("practice-proxy bond DV01", num(step_result(pack, "DV01")), 6.2*50e6*0.0001)
check("practice-proxy bond shock P&L", num(step_result(pack, "shock")), -6.2*50e6*0.0001*25)
bond_base = {
    "schemaVersion": "tpl.bond.input.v1", "settlementDate": "2026-07-31",
    "maturityDate": "2036-07-31", "dayCount": "ACT/ACT ICMA",
    "couponRate": 0.05, "couponFrequency": 2, "quoteMode": "yield",
    "yieldToMaturity": 0.05, "cleanPrice": None, "currency": "EUR",
    "notional": 1_000_000, "position": "long", "shockBp": 25,
}
bond_par = analyze_bond(bond_base)
check("canonical par clean price", bond_par["quote"]["cleanPricePer100"], 100.0, tol=1e-11)
check("canonical par dirty price", bond_par["quote"]["dirtyPricePer100"], 100.0, tol=1e-11)
check("canonical par accrued", bond_par["quote"]["accruedInterestPer100"], 0.0, tol=1e-12)
bond_between = analyze_bond({**bond_base, "settlementDate": "2026-10-17", "maturityDate": "2033-01-31", "couponRate": 0.0375, "yieldToMaturity": 0.042})
check("canonical dirty-clean-accrued identity", bond_between["quote"]["dirtyPricePer100"] - bond_between["quote"]["cleanPricePer100"], bond_between["quote"]["accruedInterestPer100"], tol=1e-12)
check("canonical cash-flow DV01 reconciliation", sum(row["cashflowDv01Per100"] for row in bond_between["cashflows"]), bond_between["analytics"]["dv01Per100"], tol=1e-12)
bond_solved = analyze_bond({**bond_base, "settlementDate": "2026-09-15", "quoteMode": "clean_price", "yieldToMaturity": None, "cleanPrice": analyze_bond({**bond_base, "settlementDate": "2026-09-15", "yieldToMaturity": 0.037125})["quote"]["cleanPricePer100"]})
check("canonical clean-price/YTM round trip", bond_solved["quote"]["yieldToMaturity"], 0.037125, tol=1e-12)
check_true("canonical YTM solver residual bounded", abs(bond_solved["quote"]["solver"]["residualPer100"]) <= 1e-10, str(bond_solved["quote"]["solver"]))

print("="*72)
print("5. FX BARRIER conditional payoff")
pack = calc.build_pack(cb.seed_for_topic("barrier")[1], family_hint="fx_barrier_option")
check("barrier spot 1.05 payoff (OTM)", num(step_result(pack, "1.05")), 0.0)
check("barrier spot 1.2 payoff", num(step_result(pack, "1.2")), max(1.2-1.1, 0)*10e6)

print("="*72)
print("6. CDS: annual premium MUST differ from PV of premium leg")
pack = calc.build_pack(cb.seed_for_topic("cds")[1], family_hint="cds_cs01")
spread_bp, notional, risky_annuity = 120.0, 50e6, 4.2
check("CDS CS01", num(step_result(pack, "CS01")), risky_annuity*notional*0.0001)
annual_premium = spread_bp*0.0001*notional            # 600,000 /yr
pv_premium_leg = spread_bp*0.0001*notional*risky_annuity  # 2,520,000
annual_str = step_result(pack, "annuel") or step_result(pack, "premium annuel") or step_result(pack, "coupon")
check_true("CDS reports an ANNUAL premium step", bool(annual_str), "no annual-premium step")
if annual_str:
    check("CDS annual premium = spread*notional", num(annual_str), annual_premium, tol=1e-3)
    check_true(
        "CDS annual premium NOT conflated with PV premium leg",
        abs(num(annual_str) - pv_premium_leg) > 1.0,
        f"annual={num(annual_str)} must not equal PV leg {pv_premium_leg}",
    )
check("CDS protection-buyer shock P&L", num(step_result(pack, "shock")), risky_annuity*notional*0.0001*25)

print("="*72)
print("7. PARAMETRIC VaR: exact inverse-normal quantile per confidence + ES")
for conf, z_ref in [(90.0, n_inv(0.90)), (95.0, n_inv(0.95)),
                    (97.5, n_inv(0.975)), (99.0, n_inv(0.99))]:
    seed = f"VaR parametrique portefeuille 20m volatilite 2% confiance {conf:g}% horizon 1 jour"
    pack = calc.build_pack(seed, family_hint="parametric_var")
    var_ref = 20e6 * 0.02 * math.sqrt(1) * z_ref
    check(f"VaR conf={conf:g}% uses exact z", num(step_result(pack, "VaR")), var_ref, tol=1e-3)
# Expected Shortfall present and ES > VaR
pack = calc.build_pack("VaR parametrique portefeuille 20m volatilite 2% confiance 95% horizon 1 jour",
                       family_hint="parametric_var")
es_str = step_result(pack, "shortfall") or step_result(pack, "ES")
check_true("VaR pack ships an Expected Shortfall step", bool(es_str), "no ES step")
if es_str:
    z95 = n_inv(0.95)
    es_ref = 20e6 * 0.02 * math.sqrt(1) * n_pdf(z95) / (1 - 0.95)
    check("Expected Shortfall (95%)", num(es_str), es_ref, tol=1e-2)

print("="*72)
print("8. AUTOCALL (Athena, memory coupons) scenario payoff")
pack = calc.build_pack(cb.seed_for_topic("autocall")[1], family_hint="autocall_structured")
# levels [65,102]: obs1 0.65<0.70 no coupon (memory); obs2 1.02>=0.70 pays 2 coupons, >=1.00 autocall
check("autocall obs2 coupon (memory=2x)", num(step_result(pack, "Observation 2 - coupon")), 0.06*2*1_000_000)
check("autocall total payoff", num(step_result(pack, "Payoff total")), 0.06*2*1_000_000 + 1_000_000)
check_true("autocall redeems early at obs2", bool(step_result(pack, "Observation 2 - autocall")), "no autocall step")

print("="*72)
print("9. MONTE CARLO call: deterministic + CI must bracket Black-Scholes")
p1 = calc.build_pack(cb.seed_for_topic("monte_carlo")[1], family_hint="monte_carlo_gbm")
p2 = calc.build_pack(cb.seed_for_topic("monte_carlo")[1], family_hint="monte_carlo_gbm")
mc1 = num(step_result(p1, "Prix MC"))
mc2 = num(step_result(p2, "Prix MC"))
se = num(step_result(p1, "Erreur standard"))
bs_ref_val = bs(100, 100, 0.20, 1.0, 0.05)["call"]
check_true("MC is deterministic (same seed -> same price)", abs(mc1 - mc2) < 1e-9, f"{mc1} vs {mc2}")
check_true("MC price within 3 SE of Black-Scholes", abs(mc1 - bs_ref_val) <= 3 * se, f"|{mc1:.4f}-{bs_ref_val:.4f}|={abs(mc1-bs_ref_val):.4f} > 3*SE={3*se:.4f}")
ci_line = step_result(p1, "IC 95%")
import re as _re2
ci_nums = [float(x) for x in _re2.findall(r"[-+]?\d+\.\d+", ci_line)]
if len(ci_nums) >= 2:
    lo, hi = ci_nums[-2], ci_nums[-1]
    check("MC CI half-width = 1.96*SE", (hi - lo) / 2, 1.96 * se, tol=1e-3)
    check_true("MC CI brackets Black-Scholes price", lo <= bs_ref_val <= hi, f"BS {bs_ref_val:.4f} not in [{lo:.4f},{hi:.4f}]")

print("="*72)
print("10. YIELD-CURVE: shared golden fixture, sparse swaps, repricing and forwards")
check_true(
    "shared yield-curve fixture exists",
    YIELD_CURVE_FIXTURE_PATH.is_file(),
    str(YIELD_CURVE_FIXTURE_PATH),
)
if YIELD_CURVE_FIXTURE_PATH.is_file():
    curve_fixture = json.loads(YIELD_CURVE_FIXTURE_PATH.read_text(encoding="utf-8"))
    curve_tolerances = curve_fixture["tolerances"]
    curve_results: dict[str, dict] = {}
    for curve_case in curve_fixture["cases"]:
        case_id = curve_case["id"]
        result = build_yield_curve(
            curve_case["instruments"], curve_fixture["conventions"]
        )
        curve_results[case_id] = result
        check_true(
            f"curve {case_id} converged",
            result["diagnostics"]["converged"] is True,
        )
        check_true(
            f"curve {case_id} has positive discount factors",
            result["diagnostics"]["positiveDiscountFactors"] is True,
        )
        check_true(
            f"curve {case_id} anchor count",
            len(result["anchors"]) == len(curve_case["expectedAnchors"]),
            f"got={len(result['anchors'])} expected={len(curve_case['expectedAnchors'])}",
        )
        for index, expected_anchor in enumerate(curve_case["expectedAnchors"]):
            if index >= len(result["anchors"]):
                break
            anchor = result["anchors"][index]
            check(
                f"curve {case_id} anchor {index + 1} time",
                float(anchor["time"]),
                float(expected_anchor["time"]),
                tol=1e-12,
            )
            check(
                f"curve {case_id} anchor {index + 1} DF",
                float(anchor["discountFactor"]),
                float(expected_anchor["discountFactor"]),
                tol=curve_tolerances["discountFactor"],
            )
        for repricing in result["repricing"]:
            check(
                f"curve {case_id} {repricing['instrumentId']} PV repricing",
                float(repricing["pvResidual"]),
                0.0,
                tol=curve_tolerances["repricing"],
            )
            check(
                f"curve {case_id} {repricing['instrumentId']} quote repricing",
                float(repricing["quoteResidual"]),
                0.0,
                tol=curve_tolerances["repricing"],
            )
        check(
            f"curve {case_id} max PV repricing",
            float(result["diagnostics"]["maxAbsPvResidual"]),
            0.0,
            tol=curve_tolerances["repricing"],
        )
        check(
            f"curve {case_id} max quote repricing",
            float(result["diagnostics"]["maxAbsQuoteResidual"]),
            0.0,
            tol=curve_tolerances["repricing"],
        )
        check_true(
            f"curve {case_id} is strictly deterministic",
            result
            == build_yield_curve(
                curve_case["instruments"], curve_fixture["conventions"]
            ),
        )

    flat_case = next(
        case for case in curve_fixture["cases"] if case["id"] == "flat_sparse_swaps"
    )
    flat_result = curve_results["flat_sparse_swaps"]
    for node in flat_result["curve"]:
        check(
            f"flat sparse {node['time']:g}Y annual zero",
            float(node["zeroAnnual"]),
            float(flat_case["expectedAnnualZero"]),
            tol=curve_tolerances["rate"],
        )
        check(
            f"flat sparse {node['intervalLabel']} continuous forward",
            float(node["forwardContinuous"]),
            float(flat_case["expectedContinuousForward"]),
            tol=curve_tolerances["rate"],
        )
    check_true(
        "flat sparse swaps construct every missing annual coupon",
        flat_result["diagnostics"]["interpolatedCouponCount"] == 5,
        f"got={flat_result['diagnostics']['interpolatedCouponCount']} expected=5",
    )

    current_case = next(
        case
        for case in curve_fixture["cases"]
        if case["id"] == "current_sparse_swaps"
    )
    current_result = curve_results["current_sparse_swaps"]
    for expected_node in current_case["expectedInterpolatedNodes"]:
        node = curve_node_at(current_result, float(expected_node["time"]))
        check_true(
            f"current sparse {expected_node['time']:g}Y node exists and is interpolated",
            node is not None and node["source"] == "interpolated-cashflow",
        )
        if node is not None:
            check(
                f"current sparse {expected_node['time']:g}Y interpolated DF",
                float(node["discountFactor"]),
                float(expected_node["discountFactor"]),
                tol=curve_tolerances["discountFactor"],
            )
    for expected_forward in current_case["expectedSegmentContinuousForwards"]:
        start = float(expected_forward["start"])
        end = float(expected_forward["end"])
        expected_rate = float(expected_forward["rate"])
        start_discount = curve_discount_at(current_result, start)
        end_discount = curve_discount_at(current_result, end)
        segment_forward = math.log(start_discount / end_discount) / (end - start)
        check(
            f"current sparse {start:g}Y->{end:g}Y segment forward",
            segment_forward,
            expected_rate,
            tol=curve_tolerances["rate"],
        )
        segment_nodes = [
            node
            for node in current_result["curve"]
            if float(node["intervalStart"]) >= start - 1e-12
            and float(node["intervalEnd"]) <= end + 1e-12
        ]
        check_true(
            f"current sparse {start:g}Y->{end:g}Y exposes interval forwards",
            bool(segment_nodes),
        )
        for node in segment_nodes:
            check(
                f"current sparse {node['intervalLabel']} engine forward",
                float(node["forwardContinuous"]),
                expected_rate,
                tol=curve_tolerances["rate"],
            )

    df3 = curve_discount_at(current_result, 3.0)
    df4 = curve_discount_at(current_result, 4.0)
    df5 = curve_discount_at(current_result, 5.0)
    check(
        "current sparse 4Y log-DF interpolation identity",
        df4,
        math.sqrt(df3 * df5),
        tol=curve_tolerances["interpolation"],
    )

print("="*72)
print("11. REALIZED VOLATILITY: shared fixture, five estimators and rolling")
check_true(
    "shared realized-volatility fixture exists",
    REALIZED_VOLATILITY_FIXTURE_PATH.is_file(),
    str(REALIZED_VOLATILITY_FIXTURE_PATH),
)
if REALIZED_VOLATILITY_FIXTURE_PATH.is_file():
    realized_fixture = json.loads(
        REALIZED_VOLATILITY_FIXTURE_PATH.read_text(encoding="utf-8")
    )
    realized_tolerances = realized_fixture["tolerances"]
    for realized_case in realized_fixture["cases"]:
        case_id = realized_case["id"]
        config = dict(realized_fixture["baseConfig"])
        result = analyze_realized_volatility(realized_case["rows"], config)
        repeated = analyze_realized_volatility(realized_case["rows"], config)
        reference = realized_volatility_reference(
            realized_case["rows"], int(config["annualization"])
        )
        expected = realized_case["expected"]
        check_true(
            f"realized-vol {case_id} deterministic",
            result == repeated,
        )
        check_true(
            f"realized-vol {case_id} common session count",
            result["diagnostics"]["alignedSessionCount"] == expected["n"],
            f"got={result['diagnostics']['alignedSessionCount']} expected={expected['n']}",
        )
        check(
            f"realized-vol {case_id} Yang-Zhang k",
            float(result["yangZhangK"]),
            float(expected["yangZhangK"]),
            tol=realized_tolerances["yangZhangK"],
        )
        check(
            f"realized-vol {case_id} independent Yang-Zhang k",
            float(result["yangZhangK"]),
            float(reference["k"]),
            tol=realized_tolerances["yangZhangK"],
        )
        for estimator in expected["dailyVariance"]:
            summary = result["summary"][estimator]
            check(
                f"realized-vol {case_id} {estimator} fixture variance",
                float(summary["dailyVariance"]),
                float(expected["dailyVariance"][estimator]),
                tol=realized_tolerances["variance"],
            )
            check(
                f"realized-vol {case_id} {estimator} independent variance",
                float(summary["dailyVariance"]),
                float(reference["variances"][estimator]),
                tol=realized_tolerances["variance"],
            )
            check(
                f"realized-vol {case_id} {estimator} fixture annual vol",
                float(summary["annualizedVol"]),
                float(expected["annualizedVol"][estimator]),
                tol=realized_tolerances["annualizedVol"],
            )
            check(
                f"realized-vol {case_id} {estimator} independent annual vol",
                float(summary["annualizedVol"]),
                float(reference["annualized"][estimator]),
                tol=realized_tolerances["annualizedVol"],
            )
        result_codes = {
            item["code"] for item in result["diagnostics"]["warnings"]
        } | {item["code"] for item in result["diagnostics"]["events"]}
        for warning_code in expected.get("warningCodes", []):
            check_true(
                f"realized-vol {case_id} warning {warning_code}",
                warning_code in result_codes,
            )
        if expected.get("rollingLast"):
            rolling_expected = expected["rollingLast"]
            rolling_actual = result["rolling"][-1]
            check_true(
                f"realized-vol {case_id} rolling date",
                rolling_actual["endDate"] == rolling_expected["date"],
            )
            for estimator in expected["dailyVariance"]:
                check(
                    f"realized-vol {case_id} rolling {estimator}",
                    float(rolling_actual["estimators"][estimator]["annualizedVolatility"]),
                    float(rolling_expected[estimator]),
                    tol=realized_tolerances["annualizedVol"],
                )
        if expected.get("annualizedVol365"):
            result_365 = analyze_realized_volatility(
                realized_case["rows"], {**config, "annualization": 365}
            )
            for estimator, expected_365 in expected["annualizedVol365"].items():
                check(
                    f"realized-vol {case_id} 365 {estimator}",
                    float(result_365["summary"][estimator]["annualizedVol"]),
                    float(expected_365),
                    tol=realized_tolerances["annualizedVol"],
                )
                check(
                    f"realized-vol {case_id} sqrt(365/252) {estimator}",
                    float(result_365["summary"][estimator]["annualizedVol"])
                    / float(result["summary"][estimator]["annualizedVol"]),
                    math.sqrt(365 / 252),
                    tol=realized_tolerances["annualizedVol"],
                )

print("="*72)
print("12. VOL SURFACE: total variance, bilinear interpolation and arbitrage flags")
surface_quotes = []
for maturity in [0.25, 0.5, 1.0, 2.0]:
    forward = 100 * math.exp(0.02 * maturity)
    discount_factor = math.exp(-0.03 * maturity)
    for log_moneyness in [-0.3, -0.15, 0.0, 0.15, 0.3]:
        volatility = 0.2 - 0.06 * log_moneyness + 0.1 * log_moneyness ** 2 + 0.01 * math.log1p(maturity)
        surface_quotes.append({"maturity": maturity, "forward": forward, "discountFactor": discount_factor, "logMoneyness": log_moneyness, "impliedVolatility": volatility, "bidVolatility": volatility - 0.005, "askVolatility": volatility + 0.005})
surface_payload = {"schemaVersion": VOL_SURFACE_INPUT_SCHEMA, "surfaceName": "independent verifier", "asOfDate": "2026-07-19", "sourceKind": "deterministic_fixture", "interpolationMode": "total_variance_bilinear", "selectedMaturity": 0.75, "selectedLogMoneyness": 0.075, "quotes": surface_quotes}
surface_result = analyze_vol_surface(surface_payload)
check_true("vol-surface clean discrete status", surface_result["quality"]["status"] == "PASS")
check("vol-surface node w=sigma^2*T", surface_result["points"][7]["totalVariance"], surface_quotes[7]["impliedVolatility"] ** 2 * surface_quotes[7]["maturity"], tol=1e-12)
variance_low = sum(surface_result["slices"][1]["points"][index]["totalVariance"] for index in [2, 3]) / 2
variance_high = sum(surface_result["slices"][2]["points"][index]["totalVariance"] for index in [2, 3]) / 2
check("vol-surface independent bilinear total variance", surface_result["selectedPoint"]["totalVariance"], (variance_low + variance_high) / 2, tol=1e-12)
calendar_payload = json.loads(json.dumps(surface_payload))
for quote in calendar_payload["quotes"]:
    if quote["maturity"] == 1.0:
        quote["impliedVolatility"] = 0.1 + 0.01 * quote["logMoneyness"] ** 2
        quote["bidVolatility"] = quote["impliedVolatility"] - 0.005
        quote["askVolatility"] = quote["impliedVolatility"] + 0.005
calendar_result = analyze_vol_surface(calendar_payload)
check_true("vol-surface five calendar flags retained", sum(row["code"] == "CALENDAR_VARIANCE_VIOLATION" for row in calendar_result["diagnostics"]) == 5)

print("="*72)
print("13. CANONICAL BLACK-SCHOLES: limits, IV, signed risk and grids")
canonical_bs_input = {
    "schemaVersion": BLACK_SCHOLES_INPUT_SCHEMA,
    "quoteMode": "volatility",
    "optionType": "call",
    "spot": 100.0,
    "strike": 100.0,
    "maturityYears": 0.5,
    "dayCount": "ACT/365F",
    "riskFreeRate": 0.02,
    "dividendYield": 0.0,
    "volatility": 0.2,
    "marketPrice": None,
    "currency": "EUR",
    "position": "long",
    "quantity": 10.0,
    "multiplier": 100.0,
    "shocks": {"spotPct": 10.0, "volPoints": 5.0, "days": 30.0},
}
canonical_bs = analyze_black_scholes(canonical_bs_input)
canonical_ref = bs(100.0, 100.0, 0.2, 0.5, 0.02)
check("canonical BS ATM call vs independent closed form", canonical_bs["call"]["unitPrice"], canonical_ref["call"], tol=5e-7)
check("canonical BS ATM put vs independent closed form", canonical_bs["put"]["unitPrice"], canonical_ref["put"], tol=5e-7)
check_true("canonical BS call-put parity", canonical_bs["parity"]["holds"] and abs(canonical_bs["parity"]["residual"]) <= 2e-12)
zero_vol = analyze_black_scholes({**canonical_bs_input, "spot": 120.0, "maturityYears": 2.0, "riskFreeRate": 0.04, "dividendYield": 0.01, "volatility": 0.0})
zero_vol_ref = max(120.0 * math.exp(-0.01 * 2.0) - 100.0 * math.exp(-0.04 * 2.0), 0.0)
check("canonical BS sigma=0 discounted limit", zero_vol["call"]["unitPrice"], zero_vol_ref, tol=1e-12)
forward_atm_spot = canonical_bs_input["strike"] * math.exp(
    (canonical_bs_input["dividendYield"] - canonical_bs_input["riskFreeRate"])
    * canonical_bs_input["maturityYears"]
)
forward_atm = analyze_black_scholes({**canonical_bs_input, "spot": forward_atm_spot, "volatility": 0.0})
check_true(
    "canonical BS sigma=0 forward-ATM kink convention",
    forward_atm["call"]["unitPrice"] == 0.0
    and abs(forward_atm["call"]["greeks"]["delta"] - 0.5) <= 1e-14
    and forward_atm["call"]["greeks"]["gamma"] == 0.0
    and forward_atm["call"]["greeks"]["vega"] == 0.0
    and "symmetric_limiting_convention" in forward_atm["conventions"]["zeroVolatilityKinkLimit"],
)
expiry = analyze_black_scholes({**canonical_bs_input, "maturityYears": 0.0, "spot": 120.0})
check_true("canonical BS expiry intrinsic and delta", expiry["call"]["unitPrice"] == 20.0 and expiry["call"]["greeks"]["delta"] == 1.0)
inverted = analyze_black_scholes({**canonical_bs_input, "quoteMode": "market_price", "volatility": None, "marketPrice": canonical_bs["call"]["unitPrice"]})
check("canonical BS implied-vol round trip", inverted["quote"]["impliedVolatility"], 0.2, tol=2e-11)
short = analyze_black_scholes({**canonical_bs_input, "position": "short"})
check_true("canonical BS signed portfolio Greeks", all(abs(short["selected"]["portfolioGreeks"][key] + canonical_bs["selected"]["portfolioGreeks"][key]) <= 1e-9 for key in canonical_bs["selected"]["portfolioGreeks"]))
check_true("canonical BS 21-point grids", all(len(rows) == 21 for rows in canonical_bs["sensitivities"].values()))

print("="*72)
print("14. IMPLIED VOL: invert BS price back to sigma")
pack = calc.build_pack(cb.seed_for_topic("vol_smile")[1], family_hint="implied_vol_smile")
iv_line = step_result(pack, "Inversion")
iv = float(_re.search(r"([\d.]+)%", iv_line).group(1)) / 100
check("implied vol of a 10.4506 ATM call", iv, 0.20, tol=1e-3)

print("="*72)
print("15. SCENARIO VARIETY: every topic x variant yields a verified, non-generic pack")
import random as _rnd
TOPICS = ["vanilla_bs", "greeks", "swap", "bond", "barrier", "cds", "var",
          "yield_curve", "autocall", "monte_carlo", "vol_smile", "stochastic"]
variety_ok = 0
variety_total = 0
for tk in TOPICS:
    seen_seeds = set()
    for v in range(6):
        rng = _rnd.Random(1000 + v)
        sc = cb.varied_scenario(tk, rng)
        variety_total += 1
        if not sc:
            FAILURES.append(f"variety {tk} v{v}: no scenario")
            continue
        fam, seed_text = sc
        seen_seeds.add(seed_text)
        pack = calc.build_pack(seed_text, family_hint=fam)
        if pack.family == "generic" or not pack.steps:
            FAILURES.append(f"variety {tk} v{v}: generic/empty pack from '{seed_text}'")
        else:
            variety_ok += 1
    CHECKS += 1
    distinct = len(seen_seeds)
    if distinct < 3:
        FAILURES.append(f"variety {tk}: only {distinct} distinct scenarios across 6 draws (too repetitive)")
        print(f"  [FAIL] {tk}: {distinct} distinct / 6")
    else:
        print(f"  [ok ] {tk}: {distinct} distinct scenarios / 6, all verified")
# spot-check vanilla numeric correctness holds across a varied scenario
sc = cb.varied_scenario("vanilla_bs", _rnd.Random(42))
import re as _re3
fam, seed_text = sc
m = {k: float(v) for k, v in _re3.findall(r"(spot|strike|vol|maturite|taux)\s*([\d.]+)", seed_text)}
pack = calc.build_pack(seed_text, family_hint=fam)
ref_call = bs(m["spot"], m["strike"], m["vol"]/100, m["maturite"], m["taux"]/100)["call"]
check(f"varied vanilla call ({seed_text[:40]}...)", num(step_result(pack, "Prix call")), ref_call, tol=1e-2)

print("="*72)
print("16. TOPIC ROUTING: requests must map to the RIGHT calculator family")
ROUTING = [
    # (topic, product, expected_topic_key)
    ("Vanilla options quote", "European call", "vanilla_bs"),
    ("Options book greeks pnl", "options book", "greeks"),
    ("Rates swaps dv01", "payer swap", "swap"),
    ("Yield curve bootstrapping", "par swaps", "yield_curve"),   # must NOT be swap
    ("Fixed income bonds duration", "bond", "bond"),
    ("Barrier options gap risk", "FX barrier", "barrier"),
    ("Structured products autocall", "Athena autocall", "autocall"),
    ("Implied volatility smile", "vanilla call", "vol_smile"),   # must NOT be vanilla_bs
    ("Monte carlo pricing", "european call", "monte_carlo"),
    ("Stochastic calculus for hedging", "ito", "stochastic"),
    ("Credit derivatives cds", "single-name CDS", "cds"),
    ("Market risk var stress", "portfolio", "var"),
]
for topic, product, expected in ROUTING:
    got = cb.detect_topic_key(topic, product, [])
    check_true(f"route '{topic}' -> {expected}", got == expected, f"got {got}")

print("="*72)
if FAILURES:
    print(f"RESULT: {len(FAILURES)} FAILURE(S) of {CHECKS} checks")
    for f in FAILURES:
        print("  -", f)
    sys.exit(1)
print(f"RESULT: ALL {CHECKS} terminal-condition checks PASSED")
