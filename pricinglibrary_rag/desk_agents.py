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
import re
from copy import deepcopy
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

from .desk_state import bs
from .tool_registry import DESK_ROLES, role_tool_names
from .trusted_analytics import option_analysis, autocall_analysis, number, swap_analysis, cds_analysis


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
    ctx.setdefault("audit", []).append({"agent": agent.name, "desk": agent.desk, "tool": tool, "ok": data is not None,
                                      "execution_path":"local_desk_helper","registry_adapter_executed":False})


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
        _log(ctx, self, "simulated_teaching_snapshot", snap)
        return {"output": f"Using {self.desk} teaching inputs ({', '.join(snap.get('curves', []))}); live-data quality is not assessed.", "data": snap}


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
        _sync_contract_spec(ctx['product_spec'],pricing)
        spec=ctx['product_spec'];horizon=f"{spec['maturity_years']:.12g} Years"
        ctx['parsed'].update({'underlying':spec['underlying'],'horizon':horizon,'months':12*spec['maturity_years']})
        ctx['rfq'].update({'underlying':spec['underlying'],'horizon':horizon})
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
        detail="No risk limit was supplied; no approval is issued." if risk['limit_usage'] is None else f"The supplied scenario uses {risk['limit_usage']*100:.1f}% of the supplied limit; no production approval is issued."
        return {"output": f"Dominant risk: {risk['dominant_risk']}. {detail}", "data": risk}


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
def _sync_contract_spec(spec:dict,pricing:dict)->None:
    """Describe the validated contract that was actually priced, not a preset.

    Moneyness uses intrinsic spot (or forward for Black-76), not delta or an
    invented 'near ATM' tolerance. The input snapshot is identical in both DTOs.
    """
    calculation=pricing.get('calculation') or {};inputs=calculation.get('inputs')
    if not isinstance(inputs,dict):raise ValueError('Computed contract inputs are required to describe an RFQ.')
    spec['inputs']=deepcopy(inputs);spec['maturity_years']=inputs['maturityYears'];spec['maturityYears']=inputs['maturityYears']
    spec['currency']=inputs['currency']
    tenor=f"{inputs['maturityYears']:.12g}Y"
    if spec['kind']=='option':
        kind=inputs['optionType'];strike=inputs['strike']
        basis='forward' if 'Black-76' in calculation.get('model','') else 'spot'
        underlying=inputs[basis];atm=math.isclose(underlying,strike,rel_tol=1e-10,abs_tol=1e-12)
        intrinsic=underlying-strike if kind=='call' else strike-underlying
        moneyness='ATM' if atm else 'ITM' if intrinsic>0 else 'OTM'
        spec.update({'optionType':kind,'option_type':kind,'strike':strike,'spot':inputs['spot'],
                     'volatility':inputs['volatility'],'riskFreeRate':inputs['riskFreeRate'],
                     'dividendYield':inputs['dividendYield'],'moneyness':moneyness,'moneyness_basis':basis,
                     'strike_over_underlying':strike/underlying})
        if basis=='forward':spec['forward']=inputs['forward']
        spec['type']=f"{spec['underlying']} European {kind.capitalize()} - K {strike:.12g}, {tenor}, {moneyness} by {basis}"
        symbol='F_T' if basis=='forward' else 'S_T'
        payoff=f'max({symbol} - K, 0)' if kind=='call' else f'max(K - {symbol}, 0)'
        spec['payoff_description']=f"quantity * {payoff}; K={strike:.12g}, European exercise at T={inputs['maturityYears']:.12g} years"
    elif spec['kind']=='swap':
        direction=inputs['direction']
        spec.update({'direction':direction,'fixedRate':inputs['fixedRate'],'riskFreeRate':inputs['riskFreeRate']})
        spec['underlying']=f"{inputs['currency']} rates ({inputs['maturityYears']:.12g}Y)"
        spec['type']=f"{inputs['currency']} {direction.capitalize()} Swap - {tenor}, fixed {inputs['fixedRate']*100:.12g}%"
        spec['payoff_description']='notional * annuity * '+('(fixed - par)' if direction=='receiver' else '(par - fixed)')
    elif spec['kind']=='cds':
        spec.update({key:inputs[key] for key in ('spread','coupon','recovery','riskFreeRate')})
        spec['position']='protection_buyer'
        spec['type']=f"{spec['underlying']} CDS Protection Buyer - {tenor}, fixed premium {inputs['coupon']*100:.12g}%"
        spec['payoff_description']=f"protection buyer receives (1 - recovery) * notional on default, pays fixed annual premium {inputs['coupon']*100:.12g}%"
    elif spec['kind']=='exotic':
        fields=('couponRate','couponBarrier','autocallBarrier','protectionBarrier','observationsPerYear','referenceSpot','spot')
        spec.update({key:inputs[key] for key in fields});spec['coupon_memory']=True
        spec['observation_times_years']=deepcopy(calculation['observation_times_years'])
        spec['type']=f"{spec['underlying']} Autocall (memory coupon) - {tenor}, coupon {inputs['couponRate']*100:.12g}% p.a."
        spec['payoff_description']=(f"{inputs['observationsPerYear']} observations/year; memory coupon {inputs['couponRate']*100:.12g}% p.a.; "
            f"autocall {inputs['autocallBarrier']*100:.12g}%, coupon barrier {inputs['couponBarrier']*100:.12g}%, terminal protection barrier {inputs['protectionBarrier']*100:.12g}% of reference spot")
    summary={key:deepcopy(spec[key]) for key in ('type','kind','underlying','currency','maturityYears','optionType','strike','spot','forward','moneyness','moneyness_basis','quantity','notional','notional_currency','direction','fixedRate','coupon','recovery','couponRate','couponBarrier','autocallBarrier','protectionBarrier','observationsPerYear') if key in spec}
    spec['contract_summary']=summary;pricing['contract_summary']=deepcopy(summary)


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


def _tools_for_desk(desk: str) -> dict[str, list[str]]:
    return {role: role_tool_names(role, desk=desk) for role in DESK_ROLES}


# ---- shared quote builder --------------------------------------------------
def _quote(pricing: dict, spec: dict, margin: float) -> dict:
    theo = float(pricing.get("theoretical_price", 0.0))
    half = max(0.02, abs(theo) * margin) if spec["kind"] in ("option", "exotic") else 0.02
    return {"theoretical": round(theo, 4), "bid": round(theo - half, 4), "ask": round(theo + half, 4),
            "mid": round(theo, 4), "spread": round(2 * half, 4), "currency": pricing.get("currency", "USD"),
            "hedge_plan": pricing.get("hedge_hint", "Hedge first-order risk, then monitor convexity/vega.")}


def _scenario_risk(spec,pricing,dominant):
    g=pricing.get("greeks",{})
    scale=1  # Pricing adapters expose position Greeks, including contract quantity.
    # Explicit educational sensitivity stress, not a VaR or a real approval.
    vega=float(g.get("vega") or 0)*scale
    dv01=float(g.get("dv01") or 0);cs01=float(g.get("cs01") or 0)
    stress_loss=-(abs(vega)*5+abs(dv01)*100+abs(cs01)*50)
    supplied_limit=spec.get("risk_limit")
    limit=number(supplied_limit,"riskLimit",1e-8,1e15) if supplied_limit is not None else None
    usage=abs(stress_loss)/limit if limit else None
    return {"dominant_risk":dominant,"dv01":dv01,"cs01":cs01,"vega":vega,"stress_loss":stress_loss,
            "limit_usage":usage,"status":"NOT_ASSESSED" if limit is None else "WITHIN_SCENARIO_LIMIT" if usage<=1 else "SCENARIO_LIMIT_BREACHED",
            "approved":False,"risk_limit":limit,"approval_scope":"No production or compliance approval is provided.",
            "scenario":{"volatility_points":5,"rates_bps":100,"credit_bps":50,"method":"Absolute first-order sensitivity stress; excludes cross terms and nonlinear repricing."},
            "limitations":["No supplied risk limit: usage cannot be assessed." if limit is None else "Only the supplied educational limit is checked.",
                            "Finite-difference/autocall sensitivities contain sampling error; this is not a risk-management approval."]}


# ---- RATES desk ------------------------------------------------------------
def _rates_spec(parsed):
    yrs = parsed["months"] / 12
    currency=parsed.get('ticket',{}).get('currency') or ('EUR' if re.search(r'\beur\b|euro',parsed.get('_q',''),re.I) else 'USD')
    return {"product_id": "PROD-RT", "type": "Payer Swap" if parsed["view"] == "Price increase" else "Receiver Swap",
            "kind": "swap", "underlying": f"{currency} rates ({yrs:g}Y)", "currency":currency,"notional": 1_000_000, "maturity_years": round(yrs, 6), "ticket": parsed.get("ticket", {}), "risk_limit":parsed.get("riskLimit"),
            "payoff_description": "notional * annuity * (par - fixed)"}
def _rates_market(room):
    levels={c:v['level'] for c,v in room.market.rates.items()} if room else {'USD':.0428,'EUR':.032}
    return {"curves": ["illustrative flat USD/EUR continuous yields"], "data_quality": None, "data_status":"simulated_teaching_inputs", "level":levels['USD'],'levels':levels}
def _rates_model(spec): return {"model": "Single-flat-curve discounted swap cash flows", "assumptions": ["illustrative continuous yield", "annual fixed payments with final stub"], "model_risk": "low"}
def _rates_price(spec,snap,room):
    ccy=spec['currency'];levels=snap.get('levels',{})
    if ccy not in levels and 'riskFreeRate' not in spec.get('ticket',{}):raise ValueError('Supply an explicit flat riskFreeRate for this swap currency.')
    params={"notional":spec["notional"],"maturityYears":spec["maturity_years"],"riskFreeRate":levels.get(ccy,.0428),
            "direction":"receiver" if "Receiver" in spec["type"] else "payer","currency":ccy,**spec.get("ticket",{})}
    result=swap_analysis(params)
    spec["notional"]=result["inputs"]["notional"]
    return {"theoretical_price":result["value"],"position_value":result["value"],"unit":ccy+" present value","currency":ccy,
            "greeks":result["greeks"],"inputs":result["inputs"],"calculation":result,"limitations":result["limitations"],
            "break_even":result["parRate"],"max_loss":"Adverse curve moves","max_profit":"Favourable curve moves",
            "hedge_hint":"Computed DV01 uses the disclosed flat curve; multi-curve/basis risk is outside this teaching model."}

def _rates_risk(spec, pricing):
    return _scenario_risk(spec,pricing,'DV01 / curve')


# ---- CREDIT desk -----------------------------------------------------------
def _credit_spec(parsed):
    return {"product_id": "PROD-CR", "type": "Buy CDS Protection", "kind": "cds", "underlying": "IG credit",
            "notional": 1_000_000, "maturity_years": parsed["months"]/12, "ticket": parsed.get("ticket", {}), "risk_limit":parsed.get("riskLimit"), "payoff_description": "(1-R) * notional on default"}
def _credit_market(room):
    sp = room.market.credit["IG"] if room else 120.0
    return {"curves": ["CDS spreads", "hazard curve"], "data_quality": None, "data_status":"simulated_teaching_inputs", "spread_bp": sp}
def _credit_model(spec): return {"model": "Hazard-rate / credit triangle", "assumptions": ["flat hazard", "recovery 40%"], "model_risk": "medium"}
def _credit_price(spec,snap,room):
    params={"notional":spec["notional"],"maturityYears":spec["maturity_years"],"spread":snap.get("spread_bp",120)/10000,"currency":"EUR",**spec.get("ticket",{})}
    result=cds_analysis(params);spec["notional"]=result["inputs"]["notional"]
    return {"theoretical_price":100*result["running_spread"],"position_value":result["value"],"unit":"% running spread p.a.","currency":result['inputs']['currency'],
            "greeks":result["greeks"],"inputs":result["inputs"],"calculation":result,"limitations":result["limitations"],
            "break_even":"Spread above the fixed premium improves protection-buyer PV","max_loss":"Premium and counterparty exposure",
            "max_profit":"Protection on default / spread widening","jump_to_default":result["jump_to_default"],
            "hedge_hint":"CS01 is finite-difference repricing of the disclosed flat-hazard model; basis/credit-curve calibration is not claimed."}

def _credit_risk(spec, pricing):
    return _scenario_risk(spec,pricing,'CS01 / jump-to-default')


# ---- FX desk ---------------------------------------------------------------
def _fx_spec(parsed):
    yrs = parsed["months"] / 12
    return {"product_id": "PROD-FX", "type": f"FX Option (EURUSD {parsed.get('ticket',{}).get('optionType','call')})", "kind": "option", "underlying": "EUR/USD",
            "notional": 1_000_000, "maturity_years": round(yrs, 6), "ticket": parsed.get("ticket", {}), "risk_limit":parsed.get("riskLimit"), "strike": 1.08,
            "payoff_description": "notional * max(S_T - K, 0)"}
def _fx_market(room):
    s = room.market.fx["EURUSD"] if room else 1.0712
    return {"curves": ["FX spot", "fwd points", "FX vol surface"], "data_quality": None, "data_status":"simulated_teaching_inputs", "spot": s, "vol": 0.09}
def _fx_model(spec): return {"model": "Garman–Kohlhagen", "assumptions": ["lognormal spot", "domestic (USD) & foreign (EUR) rates", "flat vol"], "model_risk": "low"}
def _fx_price(spec,snap,room):
    if spec.get('ticket',{}).get('currency','USD')!='USD':raise ValueError('EUR/USD option prices are denominated in USD per EUR; currency must be USD.')
    defaults={"spot":snap.get("spot",1.0712),"strike":spec["strike"],"maturityYears":spec["maturity_years"],
              "volatility":snap.get("vol",.09),"riskFreeRate":.03,"dividendYield":.02,"currency":"USD"}
    result=option_analysis(spec.get("ticket",{}),model="gk",defaults=defaults)
    quantity=number(spec.get("ticket",{}).get("quantity",spec.get("ticket",{}).get("notional",spec["notional"])),"quantity",1e-8,1e12)
    spec["quantity"]=quantity;spec["notional"]=quantity;spec["notional_currency"]="EUR"
    greeks={key:value*quantity for key,value in result["greeks"].items()}
    return {"theoretical_price":result["value"],"position_value":result["value"]*quantity,"unit":"/ EUR","currency":"USD","greeks":greeks,
            "break_even":result["inputs"]["strike"]+(1 if result['inputs']['optionType']=='call' else -1)*result["value"],"max_loss":result["value"]*quantity,"max_profit":"unlimited" if result['inputs']['optionType']=='call' else result['inputs']['strike']*quantity,
            "hedge_hint":"Domestic/foreign continuous rates are retained explicitly; delta hedge with spot and monitor vega.",
            "inputs":result["inputs"],"calculation":result,"limitations":result["limitations"]}

def _fx_risk(spec, pricing):
    return _scenario_risk(spec,pricing,'FX delta / vega')


# ---- EXOTICS desk ----------------------------------------------------------
def _exotic_spec(parsed):
    yrs = parsed["months"] / 12
    return {"product_id": "PROD-EX", "type": "Autocall (Athena, memory coupon)", "kind": "exotic", "underlying": parsed["underlying"],
            "notional": 1_000_000, "maturity_years": round(yrs, 6), "ticket": parsed.get("ticket", {}), "risk_limit":parsed.get("riskLimit"), "autocall":parsed.get("autocall",{}),
            "payoff_description": "autocall barrier 100%, coupon barrier 70%, protection 60%, memory coupons"}
def _exotic_market(room):
    return {"curves": ["supplied constant volatility", "flat continuous rate/carry"], "data_quality": None, "data_status":"simulated_teaching_inputs", "vol": 0.22, "corr": None}
def _exotic_model(spec):
    return {"model":"Single-asset risk-neutral GBM Monte Carlo, discrete observations",
            "assumptions":["constant annual volatility; no calibrated smile or LSV","discrete memory coupons and autocall dates; terminal protection only"],
            "model_risk":"high","scope":"Educational original model; no correlation sensitivity or executable market quote."}

def _exotic_price(spec,snap,room):
    ticket=spec.get("ticket",{})
    params={"maturityYears":spec["maturity_years"],"notional":spec["notional"],**spec.get("autocall",{})}
    params.update({k:v for k,v in ticket.items() if k in {"spot","referenceSpot","volatility","riskFreeRate","dividendYield","maturityYears","notional","currency"}})
    if "spot" in ticket and "referenceSpot" not in ticket:params["referenceSpot"]=ticket["spot"]
    result=autocall_analysis(params)
    spec['notional']=result['inputs']['notional'];spec['notional_currency']=result['inputs']['currency']
    return {"theoretical_price":result["value"],"position_value":result["present_value"],"unit":"% of par","currency":result['inputs']['currency'],"greeks":result["greeks"],
            "break_even":"Path-dependent; no single break-even","max_loss":params.get("notional",spec["notional"]),
            "max_profit":"Coupons and early redemption depend on the disclosed observation schedule.",
            "hedge_hint":"Inspect calculated scenario risk and Monte Carlo uncertainty; a single-asset model has no correlation hedge.",
            "calculation":result,"inputs":result["inputs"],"limitations":result["limitations"]}

def _exotic_risk(spec, pricing):
    return _scenario_risk(spec,pricing,'vega / barrier / gap')


# ---- COMMODITIES desk (oil/gold options — the mockup's WTI example) -------
def _comm_spec(parsed):
    yrs = parsed["months"] / 12
    u = parsed["underlying"]
    kind=parsed.get('ticket',{}).get('optionType','call')
    return {"product_id": "PROD-CM", "type": f"{u} {kind.capitalize()} Option",
            "kind": "option", "underlying": u, "notional": 100, "maturity_years": round(yrs, 6), "ticket": parsed.get("ticket", {}), "risk_limit":parsed.get("riskLimit"), "strike": 80.0,
            "payoff_description": "max(S_T - K, 0) per barrel"}
def _comm_market(room):
    spot = room.market.spots.get("WTI", 78.42) if room else 78.42
    return {"curves": ["commodity fwd", "vol surface"], "data_quality": None, "data_status":"simulated_teaching_inputs", "spot": spot, "vol": 0.1341}
def _comm_model(spec): return {"model": "Black-76 (lognormal futures)", "assumptions": ["lognormal forward price", "flat vol", "discount at r"], "model_risk": "low"}
def _comm_price(spec,snap,room):
    supplied=spec.get("ticket",{})
    defaults={"forward":80.0,"strike":spec["strike"],"riskFreeRate":.04,"volatility":.1341,"maturityYears":spec["maturity_years"],"currency":"USD"}
    result=option_analysis(supplied,model="black76",defaults=defaults)
    premium=result["value"]
    quantity=number(supplied.get("quantity",supplied['notional']/result['inputs']['forward'] if 'notional' in supplied else spec["notional"]),"quantity",1e-8,1e6)
    spec["quantity"]=quantity;spec["notional"]=quantity*result['inputs']['forward'];spec['notional_currency']=result['inputs']['currency']
    unit='/ oz' if 'gold' in spec['underlying'].lower() else '/ bbl'
    return {"theoretical_price":premium,"position_value":premium*quantity,"unit":unit,"currency":result['inputs']['currency'],"greeks":{k:v*quantity for k,v in result["greeks"].items()},
            "break_even":result["inputs"]["strike"]+(1 if result['inputs']['optionType']=='call' else -1)*premium,"max_loss":premium*quantity,"max_profit":"unlimited" if result['inputs']['optionType']=='call' else result['inputs']['strike']*quantity,
            "hedge_hint":"Forward delta is computed with the forward held fixed; monitor volatility and expiry risk.",
            "inputs":result["inputs"],"calculation":result,"limitations":result["limitations"]}

def _comm_risk(spec, pricing):
    return _scenario_risk(spec,pricing,'vega / gamma (commodity)')


# ---- CRYPTO VOL / OPTIONS desk (BTC/ETH options via the VolSurface engine) -
def _cvol_asset(parsed):
    return "ETH" if "eth" in (parsed.get("underlying", "").lower()) else "BTC"
def _cvol_spec(parsed):
    asset = _cvol_asset(parsed)
    yrs = max(parsed["months"] / 12, 1 / 12)
    ticket=parsed.get('ticket',{})
    kind = ticket.get('optionType',ticket.get('option_type','put' if parsed['view']=='Price decrease' else 'call'))
    return {"product_id": "PROD-CV", "type": f"{asset} European {str(kind).capitalize()} (contract inputs pending)", "kind": "option",
            "underlying": f"{asset}/USD", "asset": asset, "option_type": kind, "notional": 10,
            "maturity_years": round(yrs, 6), "ticket": parsed.get("ticket", {}), "risk_limit":parsed.get("riskLimit"), "strike": None,
            "payoff_description": (f"max(S_T - K, 0) per {asset}" if kind == "call" else f"max(K - S_T, 0) per {asset}")}
def _cvol_market(room):
    m = room.market if room else None
    spots = {a: (m.spots.get(a) if m else d) for a, d in (("BTC", 61250.0), ("ETH", 3380.0))}
    vols = {a: (m.vols.get(a) if m else d) for a, d in (("BTC", 0.55), ("ETH", 0.66))}
    return {"curves": ["simulated spot", "supplied flat volatility"], "data_quality": None, "data_status":"simulated_teaching_inputs",
            "spots": spots, "vols": vols, "spot": spots["BTC"], "vol": vols["BTC"],
            "realized_vol_30d": None,"realized_vol_status":"not_requested; use the realized-volatility calculator with explicit source rows",
            "engine": "canonical BSM; supplied teaching inputs; no provider request"}
def _cvol_model(spec):
    return {"model": "Black-Scholes-Merton with supplied flat volatility",
            "assumptions": ["log-normal spot", "supplied flat volatility; no SVI calibration claimed", "explicit continuous rate/carry"], "model_risk": "medium"}
def _cvol_price(spec,snap,room):
    if spec.get('ticket',{}).get('currency','USD')!='USD':raise ValueError('BTC/USD and ETH/USD option prices are denominated in USD; currency must be USD.')
    asset=spec.get("asset","BTC");spot=snap.get("spots",{}).get(asset) or snap.get("spot",61250)
    vol=snap.get("vols",{}).get(asset) or snap.get("vol",.55);step=500 if asset=="BTC" else 50
    defaults={"spot":spot,"strike":round(spot/step)*step,"volatility":vol,"maturityYears":spec["maturity_years"],"riskFreeRate":.04,"optionType":spec.get("option_type","call"),"currency":"USD"}
    result=option_analysis(spec.get("ticket",{}),defaults=defaults)
    supplied=spec.get('ticket',{})
    n=number(supplied.get("quantity",supplied['notional']/result['inputs']['spot'] if 'notional' in supplied else spec["notional"]),"quantity",1e-8,1e6)
    spec["quantity"]=n;spec['notional']=n*result['inputs']['spot'];spec['notional_currency']='USD'
    return {"theoretical_price":result["value"],"position_value":result["value"]*n,"unit":"/ "+asset,"currency":"USD",
            "strike":result["inputs"]["strike"],"spot":result["inputs"]["spot"],"vol":result["inputs"]["volatility"],"engine":"canonical BSM",
            "greeks":{key:value*n for key,value in result["greeks"].items()},"inputs":result["inputs"],"calculation":result,"limitations":result["limitations"],
            "break_even":result["inputs"]["strike"]+result["value"] if result["inputs"]["optionType"]=="call" else result["inputs"]["strike"]-result["value"],
            "max_loss":result["value"]*n,"max_profit":"unlimited" if result["inputs"]["optionType"]=="call" else result["inputs"]["strike"]*n,
            "hedge_hint":"Calculated flat-volatility delta/vega; no live Deribit or calibrated SVI result is claimed."}

def _cvol_risk(spec, pricing):
    return _scenario_risk(spec,pricing,'vega / gamma (crypto)')


DESKS: dict[str, DeskKit] = {
    "Commodities": DeskKit("Commodities", ["commodity option", "commodity-linked note"],
        _tools_for_desk("Commodities"),
        _comm_spec, _comm_market, _comm_model, _comm_price, _comm_risk, lambda p, s: _quote(p, s, 0.04)),
    "Rates": DeskKit("Rates", ["swap", "cap/floor", "swaption", "callable note"],
        _tools_for_desk("Rates"),
        _rates_spec, _rates_market, _rates_model, _rates_price, _rates_risk, lambda p, s: _quote(p, s, 0.04)),
    "Credit": DeskKit("Credit", ["CDS", "credit-linked note", "corporate bond"],
        _tools_for_desk("Credit"),
        _credit_spec, _credit_market, _credit_model, _credit_price, _credit_risk, lambda p, s: _quote(p, s, 0.04)),
    "FX": DeskKit("FX", ["FX forward", "FX option", "FX swap"],
        _tools_for_desk("FX"),
        _fx_spec, _fx_market, _fx_model, _fx_price, _fx_risk, lambda p, s: _quote(p, s, 0.05)),
    "Exotics": DeskKit("Exotics", ["autocall", "barrier", "range accrual", "structured note"],
        _tools_for_desk("Exotics"),
        _exotic_spec, _exotic_market, _exotic_model, _exotic_price, _exotic_risk, lambda p, s: _quote(p, s, 0.06)),
    "CryptoVol": DeskKit("CryptoVol", ["BTC/ETH option", "vol surface trade", "variance / vol swap", "structured note"],
        _tools_for_desk("CryptoVol"),
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
        # Earlier role text must describe the same final validated ticket too.
        for result in results:
            if result['role']=='Structurer':
                spec=ctx['product_spec']
                result['output']=f"Structured a {spec['type']} ({spec['payoff_description']})."
            elif result['role']=='Sales':
                rfq=ctx['rfq']
                result['output']=f"Captured RFQ on the {rfq['desk']} desk: {ctx['parsed']['intention'].lower()} on {rfq['underlying']} ({rfq['horizon']})."
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
        t=parsed.get('_q','')
        unsupported={
            'Exotics':r'\b(?:worst[- ]of|snowball|range accrual|barrier option|knock[- ](?:in|out)|basket)\b',
            'Rates':r'\b(?:swaption|cap|floor|callable|inflation|cpi)\b',
            'FX':r'\b(?:forward|fx swap)\b',
            'Credit':r'\b(?:corporate bond|credit[- ]linked note)\b',
            'CryptoVol':r'\b(?:variance swap|vol(?:atility)? swap)\b',
        }
        if (re.search(unsupported.get(desk_name,r'(?!)'),t,re.I) or
            (parsed.get('factor')=='equity' and desk_name!='Exotics')):
            raise ValueError('The requested contract has no matching RFQ pricing adapter. Its catalogue entry is retained, but no substitute product or price is returned. Available RFQ models: single-asset discrete memory-coupon autocall; flat-curve swap; flat-hazard CDS; EURUSD European option; commodity forward option; BTC/ETH European option. Use the canonical calculators for other supported numerical contracts.')
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
