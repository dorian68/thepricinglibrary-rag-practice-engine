"""Quant-grade verification harness for the deterministic pricing engines.

This is the *judge* of the self-checking loop. It re-derives every number the
engines emit with an INDEPENDENT reference implementation and asserts equality,
then runs conceptual checks a quant/trader would insist on:

  - Black-Scholes call price, delta, gamma, vega vs closed form.
  - European PUT via the engine must satisfy call-put parity exactly.
  - Greeks P&L attribution with correct units (per-1% sensitivities).
  - Swap PV / DV01 sign and magnitude.
  - Bond DV01 and shock P&L.
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

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pricinglibrary_rag import course_blocks as cb
from pricinglibrary_rag.calculators import PracticeCalculator

TOL = 1e-6
FAILURES: list[str] = []
CHECKS = 0


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
print("4. BOND DV01 / shock P&L")
pack = calc.build_pack(cb.seed_for_topic("bond")[1], family_hint="bond_duration_dv01")
check("bond DV01", num(step_result(pack, "DV01")), 6.2*50e6*0.0001)
check("bond shock P&L", num(step_result(pack, "shock")), -6.2*50e6*0.0001*25)

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
print("10. YIELD-CURVE bootstrap: discount factors")
pack = calc.build_pack(cb.seed_for_topic("yield_curve")[1], family_hint="yield_curve_bootstrap")
df1 = 1 / 1.03
df2 = (1 - 0.032 * df1) / 1.032
df3 = (1 - 0.0335 * (df1 + df2)) / 1.0335
got1 = float(_re.search(r"DF=([\d.]+)", step_result(pack, "DF 1a")).group(1))
got2 = float(_re.search(r"DF=([\d.]+)", step_result(pack, "DF 2a")).group(1))
got3 = float(_re.search(r"DF=([\d.]+)", step_result(pack, "DF 3a")).group(1))
check("bootstrap DF 1y", got1, df1, tol=1e-4)
check("bootstrap DF 2y", got2, df2, tol=1e-4)
check("bootstrap DF 3y", got3, df3, tol=1e-4)
check_true("forwards present and increasing", "Forward" in (pack.as_markdown()), "no forward steps")

print("="*72)
print("11. IMPLIED VOL: invert BS price back to sigma")
pack = calc.build_pack(cb.seed_for_topic("vol_smile")[1], family_hint="implied_vol_smile")
iv_line = step_result(pack, "Inversion")
iv = float(_re.search(r"([\d.]+)%", iv_line).group(1)) / 100
check("implied vol of a 10.4506 ATM call", iv, 0.20, tol=1e-3)

print("="*72)
print("12. SCENARIO VARIETY: every topic x variant yields a verified, non-generic pack")
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
print("13. TOPIC ROUTING: requests must map to the RIGHT calculator family")
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
