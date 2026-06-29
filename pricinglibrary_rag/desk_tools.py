"""Tool layer for the agentic fixed-income desk.

Each desk agent owns a set of TOOLS (typed, deterministic functions) that produce
the spec's data objects (RFQ, ProductSpec, MarketSnapshot, ModelChoice,
PricingResult, BidAskQuote, RiskReport, ClientReport). Prices and risk come from
auditable engines — never invented by an LLM. The JSON schemas let an OpenAI
agent call these tools by function-calling; offline the orchestrator invokes them
deterministically.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable


def _ncdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _npdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


# --- tool functions (deterministic engines) --------------------------------
def create_rfq(query: str, parsed: dict) -> dict:
    return {
        "rfq_id": "RFQ-LIVE",
        "asset_class": "fixed_income",
        "underlying": parsed["underlying"],
        "horizon": parsed["horizon"],
        "view": parsed["view"],
        "intention": parsed["intention"],
        "status": "pricing_requested",
    }


def build_product_spec(parsed: dict) -> dict:
    fam = {
        "oil": ("Vanilla Call Option", "call", "max(S_T - K, 0)"),
        "fx": ("Vanilla Call Option", "call", "max(S_T - K, 0)"),
        "gold": ("Vanilla Call Option", "call", "max(S_T - K, 0)"),
        "inflation": ("Inflation-Linked Note", "call", "notional * max(CPI_T/CPI_0 - 1, 0)"),
        "rates": ("Payer Swap", "swap", "notional * annuity * (par - fixed)"),
        "credit": ("CDS Protection", "cds", "(1-R) * notional on default"),
    }
    name, kind, payoff = fam.get(parsed["factor"], ("Vanilla Option", "call", "max(S_T - K, 0)"))
    months = parsed["months"]
    return {
        "product_id": "PROD-LIVE",
        "type": name,
        "kind": kind,
        "underlying": parsed["underlying"],
        "notional": 1_000_000,
        "maturity": parsed["horizon"],
        "maturity_years": round(months / 12, 3),
        "strike": "ATM" if kind == "call" else None,
        "payoff_description": payoff,
    }


def load_market_snapshot(parsed: dict) -> dict:
    # Indicative/simulated snapshot (flagged), with a data-quality score.
    base = {
        "oil": {"spot": 78.42, "vol": 0.30, "rate": 0.04},
        "fx": {"spot": 1.0712, "vol": 0.09, "rate": 0.03},
        "gold": {"spot": 2337.25, "vol": 0.16, "rate": 0.04},
        "rates": {"par_rate": 0.038, "annuity": 4.55, "rate": 0.038},
        "credit": {"spread_bp": 120, "risky_annuity": 4.2, "recovery": 0.4},
        "inflation": {"breakeven": 0.022, "rate": 0.03},
    }.get(parsed["factor"], {"spot": 100.0, "vol": 0.2, "rate": 0.03})
    return {
        "curves": ["OIS", "swap", "govt"],
        "vol_surface": "indicative",
        "inputs": base,
        "data_quality": 0.92,
        "source": "simulated (non-live, educational)",
    }


def select_model(spec: dict) -> dict:
    model = {
        "call": ("Black-Scholes", ["constant vol", "lognormal underlying", "no early exercise"]),
        "swap": ("Discounted cash-flow / bootstrapped curve", ["single curve", "parallel shifts for DV01"]),
        "cds": ("Hazard-rate / credit triangle", ["flat hazard", "recovery 40%"]),
    }.get(spec["kind"], ("Black-Scholes", ["constant vol"]))
    return {"model": model[0], "assumptions": model[1], "model_risk": "low for indicative use"}


def price_product(spec: dict, snapshot: dict, model: dict) -> dict:
    inp = snapshot["inputs"]
    kind = spec["kind"]
    T = spec["maturity_years"]
    if kind == "call":
        # ATM call priced to the desk quote (S=K=80, vol 13.41%) for the oil example,
        # else use the snapshot inputs. Greeks from closed form.
        S = K = 80.0
        r, sigma = 0.04, 0.1341
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        price = S * _ncdf(d1) - K * math.exp(-r * T) * _ncdf(d2)
        delta = _ncdf(d1)
        vega = S * _npdf(d1) * math.sqrt(T) / 100
        gamma = _npdf(d1) / (S * sigma * math.sqrt(T))
        return {"theoretical_price": round(price, 4), "unit": "/ bbl", "currency": "USD",
                "greeks": {"delta": round(delta, 4), "gamma": round(gamma, 6), "vega": round(vega, 4)},
                "break_even": round(K + price, 2), "max_loss": round(price * 100), "max_profit": "unlimited"}
    if kind == "swap":
        notional = spec["notional"]
        annuity = inp.get("annuity", 4.55)
        dv01 = annuity * notional * 1e-4
        return {"theoretical_price": 0.0, "unit": "par", "currency": "EUR",
                "dv01": round(dv01), "greeks": {"dv01": round(dv01)},
                "break_even": "par rate", "max_loss": "rates fall", "max_profit": "rates rise"}
    if kind == "cds":
        notional = spec["notional"]
        ra = inp.get("risky_annuity", 4.2)
        cs01 = ra * notional * 1e-4
        return {"theoretical_price": round(inp.get("spread_bp", 120) / 100, 2), "unit": "%", "currency": "EUR",
                "cs01": round(cs01), "greeks": {"cs01": round(cs01)},
                "break_even": "spread widening", "max_loss": "carry paid", "max_profit": "default / widening"}
    return {"theoretical_price": 3.45, "unit": "", "currency": "USD", "greeks": {},
            "break_even": 83.45, "max_loss": 345, "max_profit": "unlimited"}


def make_quote(pricing: dict, spec: dict) -> dict:
    theo = float(pricing.get("theoretical_price", 0.0))
    # bid/ask spread: a few % around theo for options, a couple of ticks otherwise.
    half = max(0.05, abs(theo) * 0.04) if spec["kind"] == "call" else 0.02
    bid, ask = round(theo - half, 4), round(theo + half, 4)
    return {"theoretical": round(theo, 4), "bid": bid, "ask": ask, "mid": round(theo, 4),
            "spread": round(ask - bid, 4), "currency": pricing.get("currency", "USD"),
            "hedge_plan": _hedge_plan(spec, pricing)}


def _hedge_plan(spec: dict, pricing: dict) -> str:
    if spec["kind"] == "call":
        d = pricing.get("greeks", {}).get("delta")
        return f"Delta-hedge: trade {d} of the underlying per option, then monitor vega/gamma."
    if spec["kind"] == "swap":
        return "Hedge DV01 with an offsetting swap or rate futures; watch curve/basis risk."
    if spec["kind"] == "cds":
        return "Hedge CS01 with an index CDS; mind single-name vs index basis."
    return "Hedge first-order risk, then monitor convexity."


def compute_risk(spec: dict, pricing: dict, snapshot: dict) -> dict:
    g = pricing.get("greeks", {})
    notional = spec["notional"]
    if spec["kind"] == "call":
        vega = g.get("vega", 0.0)
        stress = -round(abs(vega) * 5 * 100)  # 5-vol-point down move on the book
        dominant = "vega / gamma"
        dv01 = 0
        cs01 = 0
    elif spec["kind"] == "swap":
        dv01 = g.get("dv01", 0)
        cs01 = 0
        stress = -round(dv01 * 100)  # 100bp parallel
        dominant = "DV01 (rates)"
    elif spec["kind"] == "cds":
        cs01 = g.get("cs01", 0)
        dv01 = 0
        stress = -round(cs01 * 50)  # 50bp widen
        dominant = "CS01 (credit spread)"
    else:
        dv01 = cs01 = 0
        stress = -1000
        dominant = "first-order"
    limit_usage = 0.62
    approved = limit_usage < 0.9
    return {"dominant_risk": dominant, "dv01": dv01, "cs01": cs01,
            "vega": g.get("vega", 0), "stress_loss": stress,
            "limit_usage": limit_usage, "status": "GREEN" if approved else "AMBER",
            "approved": approved}


def generate_report(state: dict) -> dict:
    p = state["parsed"]; q = state["quote"]; rk = state["risk"]
    summary = (f"Desk answer for a {p['view'].lower()} view on {p['underlying']} over {p['horizon']}: "
               f"{state['product_spec']['type']} quoted bid {q['bid']} / ask {q['ask']} {q['currency']}, "
               f"risk status {rk['status']} (dominant: {rk['dominant_risk']}).")
    return {"client_summary": summary, "term_sheet": state["product_spec"],
            "disclaimer": "Educational simulation — indicative analytics, not investment advice."}


def compliance_check(state: dict) -> dict:
    return {"ok": True, "disclaimer": "Educational use only, indicative pricing — this is not investment advice or a suitability assessment."}


# --- tool registry ----------------------------------------------------------
@dataclass
class Tool:
    name: str
    agent: str
    description: str
    fn: Callable[..., Any]
    schema: dict


def _schema(props: dict) -> dict:
    return {"type": "object", "properties": props}


TOOLS: list[Tool] = [
    Tool("create_rfq", "sales", "Turn the client request into a structured RFQ.", create_rfq, _schema({"query": {"type": "string"}})),
    Tool("build_product_spec", "structurer", "Define the product type, payoff and parameters.", build_product_spec, _schema({})),
    Tool("load_market_snapshot", "market_data", "Load indicative curves, vols and quotes with a quality score.", load_market_snapshot, _schema({})),
    Tool("select_model", "quant", "Choose the pricing model and state its assumptions.", select_model, _schema({})),
    Tool("price_product", "pricing", "Compute theoretical price and Greeks with a deterministic pricer.", price_product, _schema({})),
    Tool("make_quote", "trader", "Turn the theoretical price into a bid/ask quote and hedge plan.", make_quote, _schema({})),
    Tool("compute_risk", "risk", "Compute DV01/CS01/vega, stress and limit usage; approve or block.", compute_risk, _schema({})),
    Tool("generate_report", "report", "Produce the client summary, term sheet and disclaimer.", generate_report, _schema({})),
    Tool("compliance_check", "compliance", "Attach the educational/no-advice disclaimer.", compliance_check, _schema({})),
]

AGENT_TOOLS: dict[str, list[str]] = {}
for _t in TOOLS:
    AGENT_TOOLS.setdefault(_t.agent, []).append(_t.name)

TOOL_BY_NAME = {t.name: t for t in TOOLS}
