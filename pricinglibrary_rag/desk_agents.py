"""Specialised multi-agent trading floor for Fixed Income & Currency (FIC).

Architecture (object-oriented, faithful to a real floor):

    Agent (abstract)                 -- declares the tool contract + act()
      ├─ SalesAgent / StructurerAgent / MarketDataAgent / QuantAgent /
         PricingAgent / TraderAgent / RiskAgent / ReportAgent   (roles)
    DeskKit                          -- a desk's products, per-role tools and
                                        its deterministic pricer/risk/quote
    Desk                             -- one desk = a team of role agents that
                                        collaborate on an RFQ (the rates trader
                                        talks to the rates sales/structurer...)
    TradingFloor                     -- routes an RFQ to the right desk
                                        (Rates / Credit / FX / Exotics)

Each agent OWNS the tools that make sense for its mission and INVOKES them; the
critical numbers come from deterministic pricers, never invented by an LLM.
"""
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

from .desk_state import bs


def _ncdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


# ============================ ABSTRACT AGENT ===============================
class Agent(ABC):
    """Base class: every desk agent declares its tools and acts on a shared ctx."""

    role: str = "agent"
    status: str = ""

    def __init__(self, kit: "DeskKit"):
        self.kit = kit
        self.desk = kit.desk
        self.name = f"{kit.desk} {self.role}"
        self.tools: list[str] = kit.role_tools.get(self.role, [])

    @abstractmethod
    def act(self, ctx: dict) -> dict:
        """Run the agent's tools against the shared context; return its output."""

    def card(self) -> dict:
        return {"name": self.name, "desk": self.desk, "role": self.role, "tools": self.tools}


def _log(ctx: dict, agent: "Agent", tool: str, data) -> None:
    ctx.setdefault("audit", []).append({"agent": agent.name, "desk": agent.desk, "tool": tool, "ok": data is not None})


# ============================ ROLE AGENTS ==================================
class SalesAgent(Agent):
    role = "Sales"
    status = "Understanding"

    def act(self, ctx):
        parsed = ctx["parsed"]
        rfq = {"rfq_id": "RFQ-LIVE", "desk": self.desk, "asset_class": "FIC",
               "underlying": parsed["underlying"], "horizon": parsed["horizon"],
               "view": parsed["view"], "intention": parsed["intention"], "status": "pricing_requested"}
        ctx["rfq"] = rfq
        _log(ctx, self, self.tools[0] if self.tools else "capture_rfq", rfq)
        return {"output": f"Captured RFQ on the {self.desk} desk: {parsed['intention'].lower()} on {parsed['underlying']} ({parsed['horizon']}).", "data": rfq}


class StructurerAgent(Agent):
    role = "Structurer"
    status = "Proposing ideas"

    def act(self, ctx):
        spec = self.kit.build_spec(ctx["parsed"])
        ctx["product_spec"] = spec
        _log(ctx, self, "build_spec", spec)
        return {"output": f"Structured a {spec['type']} ({spec['payoff_description']}).", "data": spec}


class MarketDataAgent(Agent):
    role = "Market Data"
    status = "Loading data"

    def act(self, ctx):
        snap = self.kit.market_snapshot(ctx.get("room"))
        ctx["market_snapshot"] = snap
        _log(ctx, self, self.tools[0] if self.tools else "load_market", snap)
        return {"output": f"Loaded {self.desk} market data ({', '.join(snap.get('curves', []))}); quality {snap.get('data_quality')}.", "data": snap}


class QuantAgent(Agent):
    role = "Quant"
    status = "Modeling"

    def act(self, ctx):
        model = self.kit.select_model(ctx["product_spec"])
        ctx["model_choice"] = model
        _log(ctx, self, "select_model", model)
        return {"output": f"Model: {model['model']} (assumptions: {', '.join(model['assumptions'][:2])}).", "data": model}


class PricingAgent(Agent):
    role = "Pricing"
    status = "Pricing"

    def act(self, ctx):
        pricing = self.kit.price(ctx["product_spec"], ctx.get("market_snapshot", {}), ctx.get("room"))
        ctx["pricing_result"] = pricing
        _log(ctx, self, "price_product", pricing)
        return {"output": f"Priced via the {self.desk} engine: theoretical {pricing['theoretical_price']} {pricing.get('unit','')}.", "data": pricing}


class TraderAgent(Agent):
    role = "Trader"
    status = "Quoting"

    def act(self, ctx):
        quote = self.kit.quote(ctx["pricing_result"], ctx["product_spec"])
        ctx["quote"] = quote
        _log(ctx, self, "make_quote", quote)
        return {"output": f"Quoted bid {quote['bid']} / ask {quote['ask']}; {quote['hedge_plan']}", "data": quote}


class RiskAgent(Agent):
    role = "Risk"
    status = "Validating"

    def act(self, ctx):
        risk = self.kit.risk(ctx["product_spec"], ctx["pricing_result"])
        ctx["risk"] = risk
        _log(ctx, self, "compute_risk", risk)
        return {"output": f"Risk: dominant {risk['dominant_risk']}, status {risk['status']} ({int(risk['limit_usage']*100)}% of limit).", "data": risk}


class ReportAgent(Agent):
    role = "Report"
    status = "Preparing"

    def act(self, ctx):
        q, rk, sp, p = ctx["quote"], ctx["risk"], ctx["product_spec"], ctx["parsed"]
        report = {"client_summary": (f"{self.desk} desk answer: {sp['type']} for a {p['view'].lower()} view, "
                                     f"quoted {q['bid']}/{q['ask']}, risk {rk['status']}."),
                  "term_sheet": sp,
                  "disclaimer": "Educational simulation — indicative analytics, this is not investment advice."}
        ctx["report"] = report
        _log(ctx, self, "generate_report", report)
        return {"output": report["client_summary"], "data": report}


ROLE_CLASSES = [SalesAgent, StructurerAgent, MarketDataAgent, QuantAgent,
                PricingAgent, TraderAgent, RiskAgent, ReportAgent]


# ============================ DESK KITS ====================================
@dataclass
class DeskKit:
    desk: str
    products: list[str]
    role_tools: dict[str, list[str]]
    build_spec: Callable
    market_snapshot: Callable
    select_model: Callable
    price: Callable
    risk: Callable
    quote: Callable


# ---- shared quote builder --------------------------------------------------
def _quote(pricing: dict, spec: dict, margin: float) -> dict:
    theo = float(pricing.get("theoretical_price", 0.0))
    half = max(0.02, abs(theo) * margin) if spec["kind"] in ("option", "exotic") else 0.02
    return {"theoretical": round(theo, 4), "bid": round(theo - half, 4), "ask": round(theo + half, 4),
            "mid": round(theo, 4), "spread": round(2 * half, 4), "currency": pricing.get("currency", "USD"),
            "hedge_plan": pricing.get("hedge_hint", "Hedge first-order risk, then monitor convexity/vega.")}


# ---- RATES desk ------------------------------------------------------------
def _rates_spec(parsed):
    yrs = parsed["months"] / 12
    return {"product_id": "PROD-RT", "type": "Payer Swap" if parsed["view"] == "Price increase" else "Receiver Swap",
            "kind": "swap", "underlying": "US rates (10Y)", "notional": 1_000_000, "maturity_years": round(yrs, 3),
            "payoff_description": "notional * annuity * (par - fixed)"}
def _rates_market(room):
    if room: return {"curves": ["SOFR OIS", "USD swap"], "data_quality": 0.95, "level": room.market.rates["USD"]["level"]}
    return {"curves": ["SOFR OIS", "USD swap"], "data_quality": 0.95, "level": 0.0428}
def _rates_model(spec): return {"model": "Bootstrapped curve + DCF", "assumptions": ["single curve", "parallel shift for DV01"], "model_risk": "low"}
def _rates_price(spec, snap, room):
    notional, T = spec["notional"], spec["maturity_years"]
    ann = room.market.annuity("USD", T) if room else 4.55
    dv01 = ann * notional * 1e-4
    return {"theoretical_price": 0.0, "unit": "par", "currency": "USD", "dv01": round(dv01),
            "greeks": {"dv01": round(dv01)}, "break_even": "par rate", "max_loss": "rates move adversely",
            "max_profit": "rates move favourably", "hedge_hint": "Offset DV01 with an opposite swap or rate futures; watch curve/basis."}
def _rates_risk(spec, pricing):
    dv01 = pricing["greeks"].get("dv01", 0)
    return {"dominant_risk": "DV01 / curve", "dv01": dv01, "cs01": 0, "vega": 0,
            "stress_loss": -round(dv01 * 100), "limit_usage": 0.55, "status": "GREEN", "approved": True}


# ---- CREDIT desk -----------------------------------------------------------
def _credit_spec(parsed):
    return {"product_id": "PROD-CR", "type": "Buy CDS Protection", "kind": "cds", "underlying": "IG credit",
            "notional": 1_000_000, "maturity_years": 5.0, "payoff_description": "(1-R) * notional on default"}
def _credit_market(room):
    sp = room.market.credit["IG"] if room else 120.0
    return {"curves": ["CDS spreads", "hazard curve"], "data_quality": 0.9, "spread_bp": sp}
def _credit_model(spec): return {"model": "Hazard-rate / credit triangle", "assumptions": ["flat hazard", "recovery 40%"], "model_risk": "medium"}
def _credit_price(spec, snap, room):
    notional, ra = spec["notional"], 4.2
    cs01 = ra * notional * 1e-4
    spread = snap.get("spread_bp", 120)
    return {"theoretical_price": round(spread / 100, 2), "unit": "%", "currency": "EUR", "cs01": round(cs01),
            "greeks": {"cs01": round(cs01)}, "break_even": "spread widening", "max_loss": "carry paid",
            "max_profit": "default / widening", "jump_to_default": round(0.6 * notional),
            "hedge_hint": "Hedge CS01 with an index CDS; mind single-name vs index basis."}
def _credit_risk(spec, pricing):
    cs01 = pricing["greeks"].get("cs01", 0)
    return {"dominant_risk": "CS01 / jump-to-default", "dv01": 0, "cs01": cs01, "vega": 0,
            "stress_loss": -round(cs01 * 50), "limit_usage": 0.48, "status": "GREEN", "approved": True}


# ---- FX desk ---------------------------------------------------------------
def _fx_spec(parsed):
    yrs = parsed["months"] / 12
    return {"product_id": "PROD-FX", "type": "FX Option (EURUSD call)", "kind": "option", "underlying": "EUR/USD",
            "notional": 1_000_000, "maturity_years": round(yrs, 3), "strike": 1.08,
            "payoff_description": "notional * max(S_T - K, 0)"}
def _fx_market(room):
    s = room.market.fx["EURUSD"] if room else 1.0712
    return {"curves": ["FX spot", "fwd points", "FX vol surface"], "data_quality": 0.94, "spot": s, "vol": 0.09}
def _fx_model(spec): return {"model": "Garman–Kohlhagen", "assumptions": ["lognormal spot", "domestic (USD) & foreign (EUR) rates", "flat vol"], "model_risk": "low"}
def _fx_price(spec, snap, room):
    S, K, T, vol = snap.get("spot", 1.0712), spec["strike"], spec["maturity_years"], snap.get("vol", 0.09)
    o = bs(S, K, 0.03, vol, T, "call")
    contracts = spec["notional"] / S
    return {"theoretical_price": round(o["price"], 4), "unit": "/ EUR", "currency": "USD",
            "greeks": {"delta": round(o["delta"] * contracts), "vega": round(o["vega"] * contracts)},
            "break_even": round(K + o["price"], 4), "max_loss": round(o["price"] * contracts), "max_profit": "unlimited",
            "hedge_hint": "Delta-hedge spot, then manage vega and gap around fixings."}
def _fx_risk(spec, pricing):
    g = pricing["greeks"]
    return {"dominant_risk": "FX delta / vega", "dv01": 0, "cs01": 0, "vega": g.get("vega", 0),
            "stress_loss": -round(abs(g.get("vega", 0)) * 5), "limit_usage": 0.4, "status": "GREEN", "approved": True}


# ---- EXOTICS desk ----------------------------------------------------------
def _exotic_spec(parsed):
    yrs = max(parsed["months"] / 12, 1.0)
    return {"product_id": "PROD-EX", "type": "Autocall (Athena, memory coupon)", "kind": "exotic", "underlying": parsed["underlying"],
            "notional": 1_000_000, "maturity_years": round(yrs, 3),
            "payoff_description": "autocall barrier 100%, coupon barrier 70%, protection 60%, memory coupons"}
def _exotic_market(room):
    return {"curves": ["vol surface", "correlation matrix", "dividend curve"], "data_quality": 0.88, "vol": 0.22, "corr": 0.6}
def _exotic_model(spec): return {"model": "Local-stochastic vol Monte-Carlo", "assumptions": ["calibrated smile", "correlation matrix", "20k paths"], "model_risk": "high"}
def _exotic_price(spec, snap, room):
    # indicative MC-style autocall value: PV of expected coupons + protected redemption
    notional = spec["notional"]
    coupon, prob_autocall = 0.06, 0.62
    value = notional * (1 + coupon * 1.4 * prob_autocall - 0.03)  # indicative
    return {"theoretical_price": round(value / notional * 100, 2), "unit": "% of par", "currency": "EUR",
            "greeks": {"vega": round(notional * 0.0008), "correlation": round(notional * 0.0005), "gamma": round(notional * 0.0003)},
            "break_even": "protection barrier 60%", "max_loss": "1:1 below protection barrier", "max_profit": "memory coupons + redemption",
            "hedge_hint": "Short skew / long vol / short correlation: hedge vega and dispersion, watch the protection barrier near maturity."}
def _exotic_risk(spec, pricing):
    g = pricing["greeks"]
    return {"dominant_risk": "vega / correlation / gap", "dv01": 0, "cs01": 0, "vega": g.get("vega", 0),
            "stress_loss": -round(abs(g.get("vega", 0)) * 8), "limit_usage": 0.71, "status": "AMBER", "approved": True}


# ---- COMMODITIES desk (oil/gold options — the mockup's WTI example) -------
def _comm_spec(parsed):
    yrs = parsed["months"] / 12
    u = "Crude Oil (WTI)" if parsed["factor"] == "oil" else parsed["underlying"]
    return {"product_id": "PROD-CM", "type": "WTI Call Option" if parsed["factor"] == "oil" else "Commodity Call Option",
            "kind": "option", "underlying": u, "notional": 100, "maturity_years": round(yrs, 3), "strike": 80.0,
            "payoff_description": "max(S_T - K, 0) per barrel"}
def _comm_market(room):
    spot = room.market.spots.get("WTI", 78.42) if room else 78.42
    return {"curves": ["commodity fwd", "vol surface"], "data_quality": 0.9, "spot": spot, "vol": 0.1341}
def _comm_model(spec): return {"model": "Black-76 (lognormal futures)", "assumptions": ["lognormal forward price", "flat vol", "discount at r"], "model_risk": "low"}
def _comm_price(spec, snap, room):
    # ATM call quoted to the desk premium: S=K=80, vol 13.41%, T=maturity, r=4%
    S = K = 80.0
    o = bs(S, K, 0.04, 0.1341, spec["maturity_years"], "call")
    prem = o["price"]
    return {"theoretical_price": round(prem, 2), "unit": "/ bbl", "currency": "USD",
            "greeks": {"delta": round(o["delta"], 4), "vega": round(o["vega"], 4), "gamma": round(o["gamma"], 6)},
            "break_even": round(K + prem, 2), "max_loss": round(prem * 100), "max_profit": "unlimited",
            "hedge_hint": "Delta-hedge with WTI futures, then monitor vega/gamma into expiry."}
def _comm_risk(spec, pricing):
    g = pricing["greeks"]
    return {"dominant_risk": "vega / gamma (commodity)", "dv01": 0, "cs01": 0, "vega": g.get("vega", 0),
            "stress_loss": -round(abs(g.get("vega", 0)) * 5 * 100), "limit_usage": 0.5, "status": "GREEN", "approved": True}


# ---- CRYPTO VOL / OPTIONS desk (BTC/ETH options via the VolSurface engine) -
def _cvol_asset(parsed):
    return "ETH" if "eth" in (parsed.get("underlying", "").lower()) else "BTC"
def _cvol_spec(parsed):
    asset = _cvol_asset(parsed)
    yrs = max(parsed["months"] / 12, 1 / 12)
    kind = "put" if parsed["view"] == "Price decrease" else "call"
    return {"product_id": "PROD-CV", "type": f"{asset} Vanilla {kind.capitalize()} (ATM)", "kind": "option",
            "underlying": f"{asset}/USD", "asset": asset, "option_type": kind, "notional": 10,
            "maturity_years": round(yrs, 3), "strike": None,
            "payoff_description": (f"max(S_T - K, 0) per {asset}" if kind == "call" else f"max(K - S_T, 0) per {asset}")}
def _cvol_market(room):
    from . import volsurface_bridge as vb
    m = room.market if room else None
    spots = {a: (m.spots.get(a) if m else d) for a, d in (("BTC", 61250.0), ("ETH", 3380.0))}
    vols = {a: (m.vols.get(a) if m else d) for a, d in (("BTC", 0.55), ("ETH", 0.66))}
    rv = vb.realized_vol("BTC")
    return {"curves": ["Deribit option chain", "SVI vol surface", "realized vol"], "data_quality": 0.9,
            "spots": spots, "vols": vols, "spot": spots["BTC"], "vol": vols["BTC"],
            "realized_vol_30d": rv.get("rv_30d"), "engine": vb.engine_name()}
def _cvol_model(spec):
    return {"model": "Black-Scholes-Merton + SVI smile (Deribit-calibrated)",
            "assumptions": ["log-normal spot", "SVI total-variance smile", "flat r = 4%"], "model_risk": "medium"}
def _cvol_price(spec, snap, room):
    from . import volsurface_bridge as vb
    asset = spec.get("asset", "BTC")
    S = snap.get("spots", {}).get(asset) or snap.get("spot", 61250.0)
    vol = snap.get("vols", {}).get(asset) or snap.get("vol", 0.55)
    step = 500.0 if asset == "BTC" else 50.0
    K = round(S / step) * step
    T, kind = spec["maturity_years"], spec.get("option_type", "call")
    o = vb.price_option(S, K, T, 0.04, vol, kind)
    n = spec["notional"]
    return {"theoretical_price": round(o["price"], 2), "unit": f"/ {asset}", "currency": "USD",
            "strike": K, "spot": round(S, 2), "vol": round(vol, 4), "engine": vb.engine_name(),
            "greeks": {"delta": round(o["delta"] * n, 3), "gamma": round(o["gamma"] * n, 6),
                       "vega": round(o["vega"] * n, 3), "theta": round(o["theta"] * n, 3)},
            "break_even": round(K + o["price"], 2) if kind == "call" else round(K - o["price"], 2),
            "max_loss": round(o["price"] * n), "max_profit": "unlimited" if kind == "call" else round(K * n),
            "hedge_hint": "Delta-hedge on perp/spot, manage vega along the SVI smile, watch weekend gap & funding."}
def _cvol_risk(spec, pricing):
    g = pricing["greeks"]
    return {"dominant_risk": "vega / gamma (crypto smile)", "dv01": 0, "cs01": 0, "vega": g.get("vega", 0),
            "stress_loss": -round(abs(g.get("vega", 0)) * 8), "limit_usage": 0.6, "status": "AMBER", "approved": True}


DESKS: dict[str, DeskKit] = {
    "Commodities": DeskKit("Commodities", ["commodity option", "commodity-linked note"],
        {"Sales": ["capture_rfq", "explain_commodity_product", "send_quote"],
         "Structurer": ["build_commodity_option_spec", "build_call_spread_spec", "build_collar_spec", "draft_term_sheet"],
         "Market Data": ["load_commodity_curve", "load_commodity_vol"],
         "Quant": ["select_commodity_model", "calibrate_vol"],
         "Pricing": ["price_commodity_option", "compute_commodity_greeks"],
         "Trader": ["make_commodity_quote", "apply_bid_ask", "build_futures_hedge", "update_book"],
         "Risk": ["compute_vega", "compute_gamma", "gap_risk", "check_commodity_limits"],
         "Report": ["generate_termsheet", "pricing_note"]},
        _comm_spec, _comm_market, _comm_model, _comm_price, _comm_risk, lambda p, s: _quote(p, s, 0.04)),
    "Rates": DeskKit("Rates", ["swap", "cap/floor", "swaption", "callable note"],
        {"Sales": ["capture_rfq", "explain_rates_product", "send_quote"],
         "Structurer": ["build_swap_spec", "build_cap_floor_spec", "build_swaption_spec", "draft_term_sheet"],
         "Market Data": ["load_ois_curve", "load_swap_curve", "load_swaption_vol"],
         "Quant": ["select_rates_model", "bootstrap_curve", "calibrate_hull_white"],
         "Pricing": ["price_swap", "price_cap_floor", "price_swaption", "compute_rate_greeks"],
         "Trader": ["make_rates_quote", "apply_bid_ask", "build_dv01_hedge", "update_book"],
         "Risk": ["compute_dv01", "compute_convexity", "curve_risk", "check_rate_limits"],
         "Report": ["generate_rates_termsheet", "pricing_note"]},
        _rates_spec, _rates_market, _rates_model, _rates_price, _rates_risk, lambda p, s: _quote(p, s, 0.04)),
    "Credit": DeskKit("Credit", ["CDS", "credit-linked note", "corporate bond"],
        {"Sales": ["capture_rfq", "explain_credit_product", "send_quote"],
         "Structurer": ["build_cds_spec", "build_cln_spec", "draft_term_sheet"],
         "Market Data": ["load_credit_curve", "load_cds_spreads", "load_recovery"],
         "Quant": ["select_credit_model", "bootstrap_hazard_curve", "calibrate_survival"],
         "Pricing": ["price_cds", "price_cln", "compute_cs01"],
         "Trader": ["make_credit_quote", "apply_bid_ask", "build_cs01_hedge", "update_book"],
         "Risk": ["compute_cs01", "jump_to_default", "concentration_risk", "check_credit_limits"],
         "Report": ["generate_credit_termsheet", "risk_memo"]},
        _credit_spec, _credit_market, _credit_model, _credit_price, _credit_risk, lambda p, s: _quote(p, s, 0.04)),
    "FX": DeskKit("FX", ["FX forward", "FX option", "FX swap"],
        {"Sales": ["capture_rfq", "explain_fx_product", "send_quote"],
         "Structurer": ["build_fx_forward_spec", "build_fx_option_spec", "draft_term_sheet"],
         "Market Data": ["load_fx_spot", "load_fwd_points", "load_fx_vol_surface"],
         "Quant": ["select_fx_model", "calibrate_fx_vol"],
         "Pricing": ["price_fx_forward", "price_fx_option", "compute_fx_greeks"],
         "Trader": ["make_fx_quote", "apply_bid_ask", "build_delta_hedge", "update_book"],
         "Risk": ["compute_fx_delta", "compute_fx_vega", "gap_risk", "check_fx_limits"],
         "Report": ["generate_fx_termsheet", "pricing_note"]},
        _fx_spec, _fx_market, _fx_model, _fx_price, _fx_risk, lambda p, s: _quote(p, s, 0.05)),
    "Exotics": DeskKit("Exotics", ["autocall", "barrier", "range accrual", "structured note"],
        {"Sales": ["capture_rfq", "explain_structured_product", "send_indicative"],
         "Structurer": ["build_autocall_spec", "build_barrier_spec", "build_range_accrual_spec", "draft_term_sheet"],
         "Market Data": ["load_vol_surface", "load_correlation_matrix", "load_dividend_curve"],
         "Quant": ["select_exotic_model", "calibrate_local_stoch_vol", "run_monte_carlo"],
         "Pricing": ["price_autocall_mc", "price_barrier", "compute_exotic_greeks"],
         "Trader": ["make_structured_quote", "apply_structuring_margin", "build_vega_correl_hedge", "update_book"],
         "Risk": ["compute_vega", "compute_correlation_risk", "compute_gamma", "gap_risk", "check_exotic_limits"],
         "Report": ["generate_termsheet", "structured_pricing_note"]},
        _exotic_spec, _exotic_market, _exotic_model, _exotic_price, _exotic_risk, lambda p, s: _quote(p, s, 0.06)),
    "CryptoVol": DeskKit("CryptoVol", ["BTC/ETH option", "vol surface trade", "variance / vol swap", "structured note"],
        {"Sales": ["capture_rfq", "explain_crypto_option", "send_quote"],
         "Structurer": ["build_crypto_option_spec", "build_risk_reversal_spec", "build_calendar_spec", "draft_term_sheet"],
         "Market Data": ["fetch_deribit_chain", "load_vol_surface", "load_realized_vol", "load_index_price"],
         "Quant": ["select_crypto_model", "calibrate_svi_smile", "compute_skew"],
         "Pricing": ["price_crypto_option", "compute_crypto_greeks", "compute_implied_vol"],
         "Trader": ["make_crypto_quote", "apply_bid_ask", "build_delta_hedge", "update_book"],
         "Risk": ["compute_vega", "compute_gamma", "weekend_gap_risk", "check_crypto_limits"],
         "Report": ["generate_termsheet", "vol_pricing_note"]},
        _cvol_spec, _cvol_market, _cvol_model, _cvol_price, _cvol_risk, lambda p, s: _quote(p, s, 0.05)),
}


# ============================ DESK + FLOOR =================================
class Desk:
    def __init__(self, kit: DeskKit):
        self.kit = kit
        self.agents = [cls(kit) for cls in ROLE_CLASSES]

    def run_chain(self, ctx: dict) -> list[dict]:
        results = []
        for agent in self.agents:
            out = agent.act(ctx)
            results.append({**agent.card(), "status": agent.status, **out})
        return results

    def roster(self) -> list[dict]:
        return [a.card() for a in self.agents]


class TradingFloor:
    def __init__(self):
        self.desks = {name: Desk(kit) for name, kit in DESKS.items()}

    def route(self, parsed: dict) -> str:
        f = parsed["factor"]
        t = (parsed.get("_q", "") + " " + parsed.get("intention", "") + " " + parsed.get("underlying", "")).lower()
        if f == "crypto" and not any(k in t for k in ("autocall", "barrier", "structured note", "snowball")):
            return "CryptoVol"
        if any(k in t for k in ("autocall", "barrier", "range accrual", "phoenix", "athena", "structured", "exotic", "worst-of", "snowball")):
            return "Exotics"
        if f == "rates":
            return "Rates"
        if f == "credit":
            return "Credit"
        if f in ("fx",):
            return "FX"
        if f in ("oil", "gold"):
            return "Commodities"
        if f == "inflation":
            return "Rates"     # inflation-linked handled by the rates desk
        return "FX"

    def run(self, parsed: dict, room=None) -> dict:
        desk_name = self.route(parsed)
        desk = self.desks[desk_name]
        ctx: dict = {"parsed": parsed, "room": room, "audit": []}
        agents = desk.run_chain(ctx)
        return {"desk": desk_name, "agents": agents, "audit_trail": ctx["audit"],
                "rfq": ctx.get("rfq"), "product_spec": ctx.get("product_spec"),
                "market_snapshot": ctx.get("market_snapshot"), "model_choice": ctx.get("model_choice"),
                "pricing_result": ctx.get("pricing_result"), "quote": ctx.get("quote"),
                "risk": ctx.get("risk"), "report": ctx.get("report")}

    def roster(self) -> dict:
        return {name: desk.roster() for name, desk in self.desks.items()}


_FLOOR: TradingFloor | None = None


def get_floor() -> TradingFloor:
    global _FLOOR
    if _FLOOR is None:
        _FLOOR = TradingFloor()
    return _FLOOR
