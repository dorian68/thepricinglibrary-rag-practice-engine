"""Agentic Fixed-Income trading-room orchestrator.

A REAL multi-agent desk: each role (Sales, Structurer, Market Data, Quant,
Pricing, Trader, Risk, Report) is an independent LLM agent with its own system
prompt, chained in sequence. The agents ORCHESTRATE the workflow and explain it;
they do NOT invent prices — the Pricing agent calls a deterministic pricer
(PracticeCalculator / Black-Scholes) so every number is auditable.

Offline (TPL_LLM_PROVIDER=template) it falls back to deterministic role outputs
so the chain is fully testable without an API key; with OpenAI it is genuine AI.
"""
from __future__ import annotations

import math
import re
import json
from dataclasses import dataclass

from .calculators import PracticeCalculator
from .llm import LocalLLM


# --- deterministic request understanding (auditable, not LLM-invented) ------
def parse_request(text: str) -> dict:
    t = (text or "").lower()
    from .trusted_analytics import parse_ticket
    supplied={}
    if (text or "").lstrip().startswith("{"):
        try:
            supplied=json.loads(text)
            if not isinstance(supplied,dict):supplied={}
        except ValueError:pass
    if supplied.get("ticket") is not None and not isinstance(supplied["ticket"],dict):raise ValueError("ticket must be an object.")
    if supplied.get("autocall") is not None and not isinstance(supplied["autocall"],dict):raise ValueError("autocall must be an object.")
    ticket={**parse_ticket(text),**(supplied.get("ticket") or {})}
    underlying, factor = "Crude Oil (WTI)", "oil"
    if re.search(r"euro\s*stoxx|stoxx\s*50|sx5e",t):
        underlying,factor="Euro Stoxx 50","equity"
    elif re.search(r"s&p\s*500|\bspx\b",t):
        underlying,factor="S&P 500","equity"
    elif re.search(r"\bbtc\b|bitcoin|\beth\b|ether|crypto|deribit|altcoin", t):
        underlying = "Ethereum (ETH)" if re.search(r"\beth\b|ether", t) else "Bitcoin (BTC)"
        factor = "crypto"
    elif re.search(r"p[ée]trole|oil|wti|brent|crude|baril", t):
        underlying, factor = ("Brent Crude", "oil") if "brent" in t else ("Crude Oil (WTI)", "oil")
    elif re.search(r"\beur\s*[/_-]?\s*usd\b",t):
        underlying,factor="EUR/USD","fx"
    elif re.search(r"\bgold\b|\bor\b|once",t):
        underlying,factor="Gold","gold"
    elif re.search(r"inflation|cpi", t):
        underlying, factor = "Inflation (CPI)", "inflation"
    elif re.search(r"credit|spread|cds|d[ée]faut|default", t):
        underlying, factor = "Credit Spreads", "credit"
    elif re.search(r"\btaux\b|\brates?\b|bond|obligation|swap|callable", t):
        underlying, factor = "US Rates (10Y)", "rates"
    elif re.search(r"\bgold\b|\bor\b|once", t):
        underlying, factor = "Gold", "gold"
    elif re.search(r"\beur\s*[/_-]?\s*usd\b|\beur\b|\busd\b|\bfx\b|change|devise|dollar", t):
        underlying, factor = "EUR/USD", "fx"
    m_month = re.search(r"(\d+)\s*(mois|month)", t)
    m_year = re.search(r"(\d+)\s*(ans?|years?|y\b)", t)
    horizon = f"{m_month.group(1)} Months" if m_month else (f"{m_year.group(1)} Years" if m_year else "5 Months")
    view = "Price increase"
    if re.search(r"baiss|fall|down|drop|decreas|chut|recul|crash|krach|plunge|plummet|sell[- ]?off|selloff|tank|dump|sink|collapse|tumbl|slump|correction", t):
        view = "Price decrease"
    elif re.search(r"stable|sideways|range|flat|inchang|stagn", t):
        view = "Range / stable"
    elif re.search(r"augment|rise|monte|hauss|\bup\b|increas|widen|[ée]carte", t):
        view = "Price increase"
    intention = "Hedge / Express a view"
    if re.search(r"explain|comprendre|understand|what is|c'est quoi|apprendre|how does|fonctionne", t):
        intention = "Learn a concept"
    elif re.search(r"price|pricer|quote|cote|combien|valoris", t):
        intention = "Price a product"
    elif re.search(r"hedge|couvr|prot[ée]g|peur|afraid|worried|inqui[eè]t", t):
        intention = "Hedge / Express a view"
    months = int(re.search(r"\d+", horizon).group(0)) if re.search(r"\d+", horizon) else 5
    if "Years" in horizon:
        months *= 12
    if "maturityYears" in ticket:
        months=float(ticket["maturityYears"])*12;horizon=f"{ticket['maturityYears']} Years"
    if supplied.get("underlying"):underlying=str(supplied["underlying"])
    return {"underlying": underlying, "factor": factor, "horizon": horizon,
            "view": view, "intention": intention, "objective": "Protection / Opportunity",
            "months": months,"ticket":ticket,"autocall":supplied.get("autocall") or {},
            "riskLimit":ticket.get("riskLimit",supplied.get("riskLimit")),
            "assumption_notice":"Unspecified market inputs use explicitly disclosed educational defaults, not live quotes."}


def _norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def bs_call(S: float, K: float, r: float, sigma: float, T: float) -> float:
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return S * _norm_cdf(d1) - K * math.exp(-r * T) * _norm_cdf(d2)


def price_best_idea(parsed: dict) -> dict:
    """Legacy headline adapter delegates to the same computed RFQ pipeline."""
    from .desk_agents import get_floor
    result=get_floor().run(parsed)
    p=result['pricing_result'];s=result['product_spec']
    return {'product':s['type'],'kind':s['kind'],'est_price':p['theoretical_price'],'unit':p.get('unit',''),
            'break_even':p.get('break_even'),'max_loss':p.get('max_loss'),'max_profit':p.get('max_profit'),
            'calculation':p.get('calculation'),'maturity_y':s.get('maturity_years')}


# --- the agents -------------------------------------------------------------
@dataclass
class AgentSpec:
    key: str
    name: str
    status: str
    role: str


AGENT_SPECS = [
    AgentSpec("sales", "Sales Agent", "Understanding",
              "You are the SALES agent on a fixed-income desk. Restate the client's need in one clear sentence and name the desk task (hedge, view, pricing or education). Be concise, professional, educational."),
    AgentSpec("structurer", "Structurer", "Proposing ideas",
              "You are the STRUCTURER. Given the client's risk, propose in 1-2 sentences which product family fits and why (option, spread, collar, swap, cap, note...). Do not give prices."),
    AgentSpec("market_data", "Market Data", "Loading data",
              "You are the MARKET DATA agent. In one sentence, state which curves/vols/quotes the desk would load for this trade and that they are indicative/simulated."),
    AgentSpec("quant", "Quant Agent", "Modeling",
              "You are the QUANT. In one sentence, name the pricing model you would use (Black-Scholes, Black, Hull-White, hazard-rate...) and one key assumption. Do not give prices."),
    AgentSpec("pricing", "Pricing Agent", "Pricing",
              "You are the PRICING agent. You are GIVEN the deterministic price from the pricer. In one sentence, explain what the number means. NEVER invent or change the number."),
    AgentSpec("trader", "Trader Agent", "Quoting",
              "You are the TRADER / market maker. In one sentence, explain how you turn the theoretical price into a bid/ask (spread, inventory, hedge cost). Do not invent the theoretical price."),
    AgentSpec("risk", "Risk Manager", "Validating",
              "You are the RISK manager. Restate only the supplied computed scenario risk and limit status. If no limit is supplied, say NOT_ASSESSED. Never invent a limit or an approval."),
    AgentSpec("report", "Report Agent", "Preparing",
              "You are the REPORTING agent. In one sentence, summarise the desk's answer for the client, and add that this is an educational simulation, not investment advice."),
]


# role (lowercased, matching desk_agents role names) -> system prompt for the
# optional OpenAI narration layer.
AGENT_SPECS_BY_ROLE = {s.key.replace("_", " "): s.role for s in AGENT_SPECS}


class DeskOrchestrator:
    def __init__(self, llm: LocalLLM, calculator: PracticeCalculator | None = None) -> None:
        self.llm = llm
        self.calc = calculator or PracticeCalculator()

    def _agent_call(self, spec: AgentSpec, context: str) -> str:
        # Template provider returns a canned string -> use a deterministic, role-true
        # line so the chain is testable offline. OpenAI -> a real AI agent response.
        if getattr(self.llm, "name", "") == "template":
            return _offline_line(spec.key, context)
        prompt = f"{spec.role}\n\nDesk case:\n{context}\n\nYour one-line output:"
        try:
            out = self.llm.generate(prompt, max_tokens=90).strip()
        except Exception as exc:  # noqa: BLE001 - degrade gracefully
            out = f"[{spec.name} unavailable: {exc}]"
        return out.split("\n")[0][:280] or _offline_line(spec.key, context)

    def run(self, query: str, room=None) -> dict:
        from .desk_agents import get_floor
        from .desk_state import get_room
        from .tool_registry import get_tool_registry

        parsed = parse_request(query)
        parsed["_q"] = (query or "").lower()  # raw text for desk routing (exotics keywords)
        # Route the RFQ to the right SPECIALISED desk; that desk's role agents
        # (sales -> structurer -> quant -> ... -> trader -> risk) collaborate,
        # each invoking its own tools. The room provides the live market.
        if room is None:
            try:
                room = get_room()
            except Exception:  # noqa: BLE001
                room = None
        floor = get_floor()
        fr = floor.run(parsed, room=room)

        pr = fr["pricing_result"] or {}
        spec = fr["product_spec"] or {}
        pricing_flat = {
            "product": spec.get("type", ""), "kind": spec.get("kind", ""),
            "est_price": pr.get("theoretical_price", 0.0), "unit": pr.get("unit", ""),
            "break_even": pr.get("break_even", "—"), "max_loss": pr.get("max_loss", "—"),
            "max_profit": pr.get("max_profit", "unlimited"),
        }
        # Optional AI narration layer: when OpenAI is configured, let each agent
        # rephrase its deterministic output. Offline keeps the role-true text.
        agents = fr["agents"]
        if getattr(self.llm, "name", "") != "template":
            for a in agents:
                spec_line = AGENT_SPECS_BY_ROLE.get(a["role"].lower())
                if spec_line:
                    try:
                        a["narration"] = self.llm.generate(
                            f"{spec_line}\nDesk: {a['desk']}.\nDeterministic result: {a['output']}\nYour one-line desk note:",
                            max_tokens=80).strip().split("\n")[0][:280] or a["output"]
                        a['narration_notice']='Optional unverified language-model narration; computed output remains the financial source of truth.'
                    except Exception:  # noqa: BLE001
                        pass
        registry_report = get_tool_registry().coverage_report()
        return {
            "query": query,
            "execution_mode":"deterministic_local" if getattr(self.llm,"name","")=="template" else "deterministic_pricing_with_optional_llm_narration",
            "parsed": {k: parsed[k] for k in ("underlying", "horizon", "view", "intention", "objective", "factor")},
            "desk": fr["desk"],
            "pricing": pricing_flat,
            "rfq": fr["rfq"], "product_spec": spec, "market_snapshot": fr["market_snapshot"],
            "model_choice": fr["model_choice"], "pricing_result": pr,
            "quote": fr["quote"], "risk": fr["risk"], "report": fr["report"],
            "agents": agents, "audit_trail": fr["audit_trail"],
            "roster": floor.roster(),
            "tool_registry": {
                "agent_count": registry_report["agent_count"],
                "tool_count": registry_report["tool_count"],
                "all_ok": registry_report["all_ok"],
            },
            "disclaimer": "Educational simulation — indicative analytics, this is not investment advice.",
        }


def _offline_line(key: str, context: str) -> str:
    lines = {
        "sales": "Client need restated: this is a market-view / hedge request routed to the fixed-income desk.",
        "structurer": "Proposed family: a vanilla option (or spread/collar) that matches the expressed directional view.",
        "market_data": "Loading indicative curves, vol surface and spot quotes (simulated, flagged as non-live).",
        "quant": "Model: Black-Scholes with constant vol as a first, auditable approximation; revisit for path-dependence.",
        "pricing": "Pricer returned the figure above; it is the discounted risk-neutral expectation of the payoff.",
        "trader": "Quote built by adding a bid/ask spread around the theoretical price for inventory and hedge cost.",
        "risk": "No supplied limit has been verified by this narration helper; no risk approval is issued.",
        "report": "Summary prepared for the client. Educational simulation only, not investment advice.",
    }
    return lines.get(key, "Agent step completed.")
