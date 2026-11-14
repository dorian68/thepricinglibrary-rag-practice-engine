"""Original, deterministic English interview practice and account-owned attempts.

This module does not use a textbook corpus or an LLM. Task DTOs contain no answer
key. Numerical checks are not an assessment of written reasoning or recruitment
readiness. SQLite events preserve first attempts and correction exposure.
"""
from __future__ import annotations

from copy import deepcopy
from contextlib import contextmanager
from datetime import date, datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sqlite3
import time
from typing import Annotated, Literal
from urllib.parse import urlencode
import uuid

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator

from .black_scholes import BLACK_SCHOLES_INPUT_SCHEMA, analyze_black_scholes
from .security import ApiSecurity, AuthenticatedIdentity, IDENTITY, OPERATOR

SCHEMA = "tpl.interview-lab.v1"
Variant = Literal["primary", "transfer"]
CASE_IDS = ("call-quote", "dividend-parity", "delta-hedge", "gamma-vega", "time-rates", "quote-memo")
REVIEW_RUBRIC = [
    {"id": "assumptions", "label": "I stated the product, position, units and relevant model assumptions."},
    {"id": "decision", "label": "I connected the calculated signs and magnitudes to a desk decision."},
    {"id": "limitations", "label": "I explained a model limitation and a practical follow-up check."},
]
LIMITATIONS = [
    "Numbers are checked against a deterministic European Black-Scholes-Merton engine, not live quotes.",
    "Written reasoning is self-reviewed using a rubric; no expert review or hiring certification is provided.",
    "Independent checks mean a first attempt with no correction exposure recorded on this account. Practice is not proctored; outside exposure cannot be verified. Retries are practice, not new independent evidence.",
    "Active time is client-reported foreground activity capped by elapsed server time, not verified attendance.",
]


class StrictBody(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class TaskBody(StrictBody):
    case_id: Literal["call-quote", "dividend-parity", "delta-hedge", "gamma-vega", "time-rates", "quote-memo"]
    variant: Variant = "primary"
    client_request_id: str = Field(min_length=8, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")


FiniteAnswer = Annotated[float, Field(strict=True, allow_inf_nan=False, ge=-1e12, le=1e12)]


class AttemptBody(TaskBody):
    answers: dict[str, FiniteAnswer] = Field(min_length=1, max_length=6)
    reasoning: str = Field(min_length=40, max_length=5000)

    @field_validator("reasoning")
    @classmethod
    def require_written_attempt(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 40 or len(value.split()) < 8:
            raise ValueError("Write at least 40 characters and eight words explaining your method and decision.")
        return value


class SessionBody(TaskBody):
    active_seconds: int = Field(default=0, strict=True, ge=0, le=300)


class OnboardingBody(StrictBody):
    role: Literal["sales_trading", "structuring", "market_risk"]
    deadline: date | None = None
    minutes_per_session: Literal[15, 30, 45, 60] = 30


class ReviewCriteria(StrictBody):
    assumptions: StrictBool
    decision: StrictBool
    limitations: StrictBool


class ReviewBody(StrictBody):
    criteria: ReviewCriteria
    notes: str = Field(default="", max_length=2500)
    client_request_id: str = Field(min_length=8, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")


def _input(**overrides) -> dict:
    return {"schemaVersion": BLACK_SCHOLES_INPUT_SCHEMA, "quoteMode": "volatility",
            "optionType": "call", "spot": 100.0, "strike": 100.0,
            "maturityYears": 1.0, "dayCount": "ACT/365F", "riskFreeRate": 0.05,
            "dividendYield": 0.0, "volatility": 0.20, "marketPrice": None,
            "currency": "USD", "position": "long", "quantity": 1,
            "multiplier": 1, "shocks": {"spotPct": 5, "volPoints": 1, "days": 1},
            **overrides}


def _q(key: str, label: str, unit: str, tolerance: float, expected: float, explanation: str) -> dict:
    return {"id": key, "label": label, "unit": unit, "tolerance_abs": tolerance,
            "expected": expected, "explanation": explanation}


def _full_case(case_id: str, variant: str) -> dict:
    if case_id not in CASE_IDS:
        raise HTTPException(status_code=404, detail="Interview case not found.")
    if variant not in {"primary", "transfer"}:
        raise HTTPException(status_code=422, detail="Variant must be primary or transfer.")
    transfer = variant == "transfer"
    ticket = _input()
    questions: list[dict] = []
    if case_id == "call-quote":
        ticket = _input(optionType="put" if transfer else "call")
        result = analyze_black_scholes(ticket)["selected"]
        title = "From a call quote to a put" if transfer else "Give your first European call quote"
        summary = "Price a vanilla option and explain the units and delta."
        brief = ("An interviewer replaces the one-year call with a put on the same non-dividend-paying stock. "
                 "Compute the put premium per share and its delta. Explain why the delta sign changes while gamma stays positive."
                 if transfer else "A salesperson asks for an indicative one-year, at-the-money European call on a stock at USD 100. "
                 "You have a flat 20% annual volatility and 5% continuously compounded risk-free rate. "
                 "Compute the model premium per share and delta, then explain what a small spot rise means for a long call.")
        questions = [_q("price", "Model premium per share", "USD per share", 0.02, result["unitPrice"], "Use discounted stock and strike terms in the European BSM formula."),
                     _q("delta", "Option delta per share", "option USD / spot USD", 0.002, result["greeks"]["delta"], "Call delta is N(d1); put delta is N(d1) - 1 when dividend yield is zero.")]
        concept = "A price is currency per share. Delta is a local slope, not a probability of profit or a guaranteed hedge."
        hints = ["d1 = [ln(S/K) + (r - q + sigma²/2)T] / (sigma sqrt(T)); d2 = d1 - sigma sqrt(T).",
                 "Call = S exp(-qT)N(d1) - K exp(-rT)N(d2); use put-call parity or the corresponding put formula."]
        d1=(math.log(ticket["spot"]/ticket["strike"])+(ticket["riskFreeRate"]-ticket["dividendYield"]+0.5*ticket["volatility"]**2)*ticket["maturityYears"])/(ticket["volatility"]*math.sqrt(ticket["maturityYears"]))
        d2=d1-ticket["volatility"]*math.sqrt(ticket["maturityYears"])
        solution = (f"Substitute ln(100/100)=0, r=0.05, q=0, sigma=0.20 and T=1: d1={d1:.6f}, d2={d2:.6f}. "
                    "Discount the strike by exp(-0.05), then use the matching call/put normal-CDF terms. "
                    f"With {ticket['optionType']} exercise, price = {result['unitPrice']:.6f} USD per share and "
                    f"delta = {result['greeks']['delta']:.6f}. A USD 1 spot move gives an approximately delta-USD price move, "
                    "holding time and volatility fixed. European exercise, continuous yields, flat volatility and frictionless hedging "
                    "are model assumptions. A model mid is not a bid/offer quote; check liquidity, skew and transaction costs.")
    elif case_id == "dividend-parity":
        ticket = _input(spot=120, strike=115, maturityYears=0.75, riskFreeRate=0.03, dividendYield=0.04, volatility=0.25)
        result = analyze_black_scholes(ticket)
        rhs = ticket["spot"] * math.exp(-ticket["dividendYield"] * ticket["maturityYears"]) - ticket["strike"] * math.exp(-ticket["riskFreeRate"] * ticket["maturityYears"])
        title = "What changes when dividend carry disappears?" if transfer else "Reconcile a dividend-paying call and put"
        summary = "Use carry-adjusted parity and distinguish a yield from a cash dividend."
        brief = ("Keep spot, strike, time, rate and volatility fixed, but set the continuous dividend yield to zero. "
                 "Compute the new put price and the increase in the call price from the original 4% yield ticket. "
                 "Explain the direction of both changes. The call change is new call minus original call."
                 if transfer else "The desk has a European call on a dividend-paying stock. Reproduce its model value, "
                 "then infer the same-strike, same-expiry put through carry-adjusted put-call parity. "
                 "Report C - P separately. Explain why subtracting the nominal strike or ignoring dividends breaks parity.")
        if transfer:
            new = analyze_black_scholes({**ticket, "dividendYield": 0.0})
            questions = [_q("put_price", "Put premium with zero dividend yield", "USD per share", 0.02, new["put"]["unitPrice"], "Reprice with q = 0; keep the other inputs unchanged."),
                         _q("call_change", "Call premium change: zero yield minus original yield", "USD per share", 0.02, new["call"]["unitPrice"]-result["call"]["unitPrice"], "A lower dividend yield increases the prepaid-forward stock term and the call price.")]
        else:
            questions = [_q("put_price", "Put premium implied by parity", "USD per share", 0.02, result["put"]["unitPrice"], "P = C - S exp(-qT) + K exp(-rT)."),
                         _q("call_minus_put", "Call premium minus put premium", "USD per share", 0.02, rhs, "The difference equals discounted stock minus discounted strike, independent of volatility.")]
        concept = "Continuous dividend yield is an annual decimal carry input; actual discrete cash dividends need a suitable model."
        hints = ["C - P = S exp(-qT) - K exp(-rT).", "Changing q changes the forward and both option prices, not only the parity check."]
        solution = ("Original C - P = S exp(-qT) - K exp(-rT) = " + f"{rhs:.6f} USD per share. "
                    f"Original call = {result['call']['unitPrice']:.6f}; original put = {result['put']['unitPrice']:.6f}. "
                    "A lower continuous dividend yield raises the call and lowers the put at unchanged spot, rate, time and volatility. "
                    "Check the actual ex-dividend schedule, borrowing conditions and European exercise before using this as an arbitrage comparison.")
    elif case_id == "delta-hedge":
        ticket = _input(optionType="put" if transfer else "call", position="long" if transfer else "short", quantity=200, multiplier=100)
        result = analyze_black_scholes(ticket)["selected"]
        scale = (-1 if ticket["position"] == "short" else 1)*ticket["quantity"]*ticket["multiplier"]
        hedge = -scale*result["greeks"]["delta"]
        title = "Hedge a purchased put instead of a sold call" if transfer else "Hedge the risk, not the option name"
        summary = "Translate unit delta into a signed share hedge for a real contract size."
        brief = (f"You are {ticket['position']} {ticket['quantity']} European {ticket['optionType']} contracts, "
                 f"with {ticket['multiplier']} shares per contract. Compute the unit option delta and the stock position "
                 "that initially neutralises total portfolio delta. Positive hedge shares mean buy stock; negative means short stock. "
                 "Explain the sign from the full position, and what must be revisited after spot moves.")
        questions = [_q("option_delta", "Unit option delta before position scaling", "delta per option share", 0.002, result["greeks"]["delta"], "The unit put delta is negative; selling an option reverses the portfolio exposure, not the unit option Greek."),
                     _q("hedge_shares", "Signed stock hedge", "shares; buy + / sell -", 45, hedge, "Hedge = -position sign × contracts × multiplier × unit delta.")]
        concept = "A short call and a long put both have negative portfolio delta. A long put still has positive unit gamma."
        hints = ["Keep unit delta separate from signed portfolio delta.", "A stock share has delta +1. Set portfolio option delta + stock shares = 0."]
        solution = (f"Unit delta = {result['greeks']['delta']:.6f}. Position scale = {scale:g}; "
                    f"option portfolio delta = {-hedge:.6f} shares. Buy {hedge:.6f} shares for an initially neutral delta. "
                    "The hedge must be revisited because gamma changes delta as spot changes, and time and volatility also affect delta. "
                    "Share rounding, shorting constraints and transaction costs create residual risk; delta-neutral does not mean risk-free.")
    elif case_id == "gamma-vega":
        vol_shock = -2 if transfer else 2
        ticket = _input(position="long" if transfer else "short", quantity=40, multiplier=100,
                        shocks={"spotPct": 5, "volPoints": 2, "days": 0})
        result = analyze_black_scholes(ticket)["selected"]
        scale = (-1 if ticket["position"] == "short" else 1)*ticket["quantity"]*ticket["multiplier"]
        ds = ticket["spot"]*0.05
        gamma_pnl = 0.5*result["greeks"]["gamma"]*scale*ds*ds
        vega_pnl = result["greeks"]["vega"]*scale*vol_shock
        title = "Separate positive gamma from a falling volatility mark" if transfer else "Explain P&L after a delta hedge"
        summary = "Use signed gamma and per-vol-point vega without claiming an exact stress repricing."
        brief = (f"An initially delta-hedged {ticket['position']} call position contains 40 contracts of 100 shares. "
                 f"Spot rises by USD {ds:g} and implied volatility moves by {vol_shock:+g} percentage points, "
                 "with no elapsed time. Estimate the gamma contribution, vega contribution and their sum. "
                 "Use a second-order spot / first-order volatility Taylor approximation and omit cross terms. "
                 "Explain why the sign of gamma alone does not settle the combined P&L.")
        questions = [_q("gamma_pnl", "Gamma contribution after initial delta hedge", "USD for whole position", 2.0, gamma_pnl, "0.5 × signed portfolio gamma × (USD spot change)²."),
                     _q("vega_pnl", "Vega contribution", "USD for whole position", 2.0, vega_pnl, "Canonical vega is per +1 volatility percentage point: multiply by the shock in points, not its decimal."),
                     _q("hedged_pnl", "Approximate combined P&L", "USD for whole position", 4.0, gamma_pnl+vega_pnl, "Add gamma and vega terms; the initial stock hedge offsets only the first-order spot term.")]
        concept = "This is a local Taylor estimate. Vanna, volga, financing and hedge rebalancing are excluded; large shocks need full repricing."
        hints = ["Unit gamma has inverse-price units; unit vega is already scaled per +1 volatility percentage point.", "Reverse both Greeks when the option position is short, then apply the signed shock."]
        solution = (f"Unit gamma = {result['greeks']['gamma']:.8f} per USD and unit vega = {result['greeks']['vega']:.6f} USD per +1 volatility point. "
                    f"Position scale = {scale:g}; apply 0.5 × signed gamma × 5² and signed vega × ({vol_shock:+g}). "
                    f"Signed gamma term = {gamma_pnl:.6f} USD; signed vega term = {vega_pnl:.6f} USD; "
                    f"sum = {gamma_pnl+vega_pnl:.6f} USD. The stock hedge removes the initial linear spot exposure, "
                    "not convexity or implied-volatility risk. Quote this as an approximation, identify omitted cross terms, "
                    "and run full repricing before relying on a large stress number.")
    elif case_id == "time-rates":
        ticket = _input(optionType="put" if transfer else "call", maturityYears=0.5,
                        shocks={"spotPct": 5, "volPoints": 1, "days": 30})
        result = analyze_black_scholes(ticket)["selected"]
        later = analyze_black_scholes({**ticket,"maturityYears":ticket["maturityYears"]-30/365})["selected"]
        higher_rate = analyze_black_scholes({**ticket,"riskFreeRate":ticket["riskFreeRate"]+0.01})["selected"]
        time_pnl=later["unitPrice"]-result["unitPrice"]
        rate_pnl=higher_rate["unitPrice"]-result["unitPrice"]
        title = "Carry and rates on a put" if transfer else "Keep time decay and a rate bump separate"
        summary = "Reprice exact one-factor changes and distinguish calendar days from annual sensitivities."
        brief = (f"For the long European {ticket['optionType']} below, compare two separate scenarios with the original model premium. "
                 "Scenario A: 30 calendar days elapse under ACT/365F, all other inputs fixed. Scenario B: no time elapses, "
                 "but the continuous risk-free rate rises by 100 basis points (0.01 in decimal). "
                 "Give each exact premium change per share, rather than multiplying a Greek for a large move. "
                 "Explain why a rate rise has a different effect on a call and a put.")
        questions = [_q("time_pnl", "Exact premium change after 30 calendar days", "USD per share", 0.02, time_pnl, "Reprice at T - 30/365, then subtract the original premium."),
                     _q("rate_pnl", "Exact premium change after a +100 bp rate shift", "USD per share", 0.02, rate_pnl, "Reprice at r + 0.01 with original T; this is a separate one-factor scenario.")]
        concept = "Calendar-day theta and per-percentage-point rho are local sensitivities. These questions ask for exact finite repricing."
        hints = ["30 days is 30/365 years, not 30/252 under the declared day-count.", "Keep the two scenarios separate; do not advance time in the rate-only scenario."]
        solution = (f"Base premium = {result['unitPrice']:.6f}; after 30 days = {later['unitPrice']:.6f}, "
                    f"change {time_pnl:.6f} USD per share. At r+0.01 with unchanged maturity, premium = {higher_rate['unitPrice']:.6f}, "
                    f"change {rate_pnl:.6f} USD per share. A higher rate reduces the present value of the strike: "
                    "all else equal it helps a call and hurts a put. These are model ceteris-paribus comparisons, "
                    "not forecasts of stock/rate co-movement.")
    else:
        ticket = _input(spot=125, strike=110, maturityYears=0.75, riskFreeRate=0.03,
                        dividendYield=0.01, volatility=0.30, position="long" if transfer else "short",
                        optionType="put" if transfer else "call", quantity=50, multiplier=100,
                        shocks={"spotPct":10,"volPoints":5,"days":0})
        base = analyze_black_scholes(ticket)["selected"]
        shocked = analyze_black_scholes({**ticket,"spot":ticket["spot"]*1.10,"volatility":ticket["volatility"]+0.05})["selected"]
        sign = -1 if ticket["position"] == "short" else 1
        scale = sign*ticket["quantity"]*ticket["multiplier"]
        hedge = -scale*base["greeks"]["delta"]
        premium = -scale*base["unitPrice"]
        stress = scale*(shocked["unitPrice"]-base["unitPrice"])+hedge*(ticket["spot"]*0.1)
        title = "Defend a long put and its stock hedge" if transfer else "Deliver a quote-and-risk memo"
        summary = "Combine premium cash flow, signed hedge and a two-factor stress in a concise desk memo."
        brief = (f"You are {ticket['position']} 50 European {ticket['optionType']} contracts of 100 shares on a USD 125 stock. "
                 "Give the signed option premium cash flow (cash received positive, paid negative), "
                 "the initial signed stock hedge (buy positive), and the full-repricing combined option-and-static-stock-hedge P&L "
                 "when spot rises 10% and volatility rises 5 percentage points simultaneously, with no elapsed time. "
                 "Write a short quote-and-risk memo that names the transaction, assumptions, hedge direction, stress result "
                 "and a practical limitation. Ignore financing, spread and stock execution costs in the computed stress.")
        questions = [_q("premium", "Signed option premium cash flow", "USD; received + / paid -", 100.0, premium, "Option cash flow is minus the signed position value; buying the hedge is a separate cash flow."),
                     _q("hedge_shares", "Initial signed stock hedge", "shares; buy + / sell -", 15.0, hedge, "Hedge shares = minus signed total option delta."),
                     _q("stress_pnl", "Exact option plus static stock-hedge stress P&L", "USD for whole position", 100.0, stress, "Reprice both spot and volatility jointly; add unchanged hedge shares × spot change. Do not count initial premium again in P&L.")]
        concept = "Premium cash flow, option mark-to-market P&L and hedge financing are different quantities. A static hedge is not a dynamically rebalanced hedge."
        hints = ["For the stress use S=137.5, sigma=0.35 and the original T, r and q.", "P&L = signed quantity × multiplier × (stressed unit price - base unit price) + initial hedge shares × (stressed S - base S)."]
        solution = (f"Signed premium cash flow = {premium:.6f} USD. Initial stock hedge = {hedge:.6f} shares. "
                    f"Base option premium = {base['unitPrice']:.6f} and stressed premium = {shocked['unitPrice']:.6f} USD per share. "
                    f"Combined full-repricing P&L = {stress:.6f} USD. A defensible memo states the signed option position "
                    "and contract size, separates premium from P&L, explains the hedge sign and flags constant-volatility "
                    "model assumptions, smile dynamics, execution costs and the risk of a static hedge through a gap. "
                    "The numeric checker does not judge whether your written argument is persuasive; review it against the rubric.")
    return {"schema_version": SCHEMA, "language": "en", "id": case_id, "variant": variant,
            "order": CASE_IDS.index(case_id)+1, "title": title, "summary": summary,
            "skill": {"call-quote":"Pricing and units", "dividend-parity":"Carry and parity", "delta-hedge":"Signed hedging",
                      "gamma-vega":"Scenario risk", "time-rates":"Time and rate conventions", "quote-memo":"Quote and risk communication"}[case_id],
            "minutes": 15 if case_id == "quote-memo" else 10, "brief": brief, "ticket": ticket,
            "questions": questions, "reasoning_prompt": "Explain your method, the economic sign and your desk decision. State one model limitation. For the final case write a concise quote-and-risk memo.",
            "concept_note": concept, "hints": hints, "rubric": deepcopy(REVIEW_RUBRIC),
            "assumptions": ["European exercise; continuous rates and dividend yield; constant annual volatility.",
                            "Rates/volatility in the ticket are decimals; time is ACT/365F years; amounts are USD.",
                            "Educational model values; no live executable quote or recruitment guarantee."],
            "tool_url": "/tools/bs-pricer?"+urlencode({
                "spot":ticket["spot"],"strike":ticket["strike"],"maturityDays":365*ticket["maturityYears"],
                "riskFreeRate":100*ticket["riskFreeRate"],"dividendYield":100*ticket["dividendYield"],
                "volatility":100*ticket["volatility"],"optionType":ticket["optionType"],"position":ticket["position"],
                "quantity":ticket["quantity"],"multiplier":ticket["multiplier"],"currency":ticket["currency"],
                "spotShockPercent":ticket["shocks"]["spotPct"],"volShockPointsPercent":ticket["shocks"]["volPoints"],
                "daysShock":ticket["shocks"]["days"]}),
            "public_preview":case_id == CASE_IDS[0], "worked_solution":solution}


def case_task(case_id: str, variant: str = "primary") -> dict:
    task = _full_case(case_id, variant)
    task.pop("worked_solution")
    for question in task["questions"]:
        question.pop("expected")
        question.pop("explanation")
    return task


def catalogue() -> dict:
    cases=[]
    for case_id in CASE_IDS:
        c=case_task(case_id)
        cases.append({**{key:c[key] for key in ("id","order","title","skill","minutes","summary","public_preview")},
                      "variants":["primary","transfer"]})
    return {"schema_version":SCHEMA,"language":"en","title":"Pricing and Greeks Interview Lab",
            "access_policy":"public_first_case_signed_pilot","case_count":len(cases),"cases":cases,
            "prerequisites":["Basic option payoffs and algebra","Familiarity with annual rates and volatility"],
            "promise":"Practise six bank-derivatives interview cases, compare verified numbers, and check transfer on a changed problem.",
            "limitations":LIMITATIONS}


def _assessment(case_id: str, variant: str, answers: dict[str,float] | None = None) -> dict:
    full = _full_case(case_id,variant)
    expected_ids={q["id"] for q in full["questions"]}
    if answers is not None and set(answers) != expected_ids:
        raise HTTPException(status_code=422,detail="Answer keys must match this task exactly: "+", ".join(sorted(expected_ids)))
    checks=[]
    for q in full["questions"]:
        answer=answers[q["id"]] if answers is not None else None
        checks.append({**q,"submitted":answer,"passed":answer is not None and abs(answer-q["expected"])<=q["tolerance_abs"]})
    return {"numerical_pass":answers is not None and all(q["passed"] for q in checks),"checks":checks,
            "worked_solution":full["worked_solution"],"rubric":full["rubric"],"reasoning_reviewed":False,
            "reasoning_assessment":"Self-review only. Numerical correctness does not grade your reasoning.","limitations":LIMITATIONS}


def _stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _json(value) -> str:
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)


class InterviewLabStore:
    """Account-scoped append-only events on the existing platform SQLite file."""

    def __init__(self, db_path: str | Path):
        self.db_path=str(db_path)
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS interview_profiles (
                    owner_id TEXT PRIMARY KEY, onboarding TEXT, current_task TEXT NOT NULL,
                    active_seconds INTEGER NOT NULL DEFAULT 0, last_seen REAL NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS interview_events (
                    id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, kind TEXT NOT NULL,
                    request_id TEXT NOT NULL, request_hash TEXT NOT NULL, case_id TEXT,
                    variant TEXT, payload TEXT NOT NULL, created_at TEXT NOT NULL,
                    UNIQUE(owner_id,request_id)
                );
                CREATE INDEX IF NOT EXISTS ix_interview_owner ON interview_events(owner_id,created_at);
            """)

    @contextmanager
    def _connect(self):
        db=sqlite3.connect(self.db_path,timeout=10)
        db.row_factory=sqlite3.Row
        db.execute("PRAGMA busy_timeout=10000")
        try:
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def _ensure(db, owner: str):
        stamp=_stamp()
        db.execute("INSERT OR IGNORE INTO interview_profiles(owner_id,current_task,last_seen,created_at,updated_at) VALUES(?,?,?,?,?)",
                   (owner,_json({"case_id":CASE_IDS[0],"variant":"primary"}),time.time(),stamp,stamp))

    @staticmethod
    def _existing(db,owner,request_id,request_hash):
        row=db.execute("SELECT * FROM interview_events WHERE owner_id=? AND request_id=?",(owner,request_id)).fetchone()
        if row:
            if row["request_hash"] != request_hash:
                raise HTTPException(status_code=409,detail="This request ID was already used for a different action. Use a new request ID.")
            return json.loads(row["payload"])
        return None

    def _event(self,db,owner,kind,request_id,body,payload,case_id=None,variant=None):
        db.execute("INSERT INTO interview_events VALUES(?,?,?,?,?,?,?,?,?)",
                   (payload.get("id") or "evt_"+uuid.uuid4().hex,owner,kind,request_id,
                    hashlib.sha256(_json({"kind":kind,"body":body}).encode()).hexdigest(),case_id,variant,_json(payload),_stamp()))

    def onboarding(self,owner: str,body:OnboardingBody) -> dict:
        value=body.model_dump(mode="json")
        value["suggested_session"]={"minutes":body.minutes_per_session,
            "steps":["Attempt the call quote before seeing a correction.","Check the signs and self-review your reasoning.",
                     "Try the put transfer variant, then continue to carry and parity."],
            "schedule_note":"One primary case and its transfer variant per session; revisit errors before adding another case."}
        with self._connect() as db:
            self._ensure(db,owner)
            db.execute("UPDATE interview_profiles SET onboarding=?,updated_at=? WHERE owner_id=?",(_json(value),_stamp(),owner))
        return value

    def _write(self,owner,kind,body:TaskBody | ReviewBody,handler):
        data=body.model_dump(mode="json")
        request_hash=hashlib.sha256(_json({"kind":kind,"body":data}).encode()).hexdigest()
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._ensure(db,owner)
            old=self._existing(db,owner,body.client_request_id,request_hash)
            if old is not None:
                return old
            payload=handler(db,data)
            self._event(db,owner,kind,body.client_request_id,data,payload,data.get("case_id"),data.get("variant"))
            return payload

    def session(self,owner:str,body:SessionBody)->dict:
        def action(db,data):
            profile=db.execute("SELECT * FROM interview_profiles WHERE owner_id=?",(owner,)).fetchone()
            now=time.time()
            credited=min(body.active_seconds,max(0,int(now-profile["last_seen"])),300)
            current={"case_id":body.case_id,"variant":body.variant}
            db.execute("UPDATE interview_profiles SET current_task=?,active_seconds=active_seconds+?,last_seen=?,updated_at=? WHERE owner_id=?",
                       (_json(current),credited,now,_stamp(),owner))
            return {"current_task":current,"credited_active_seconds":credited,"persisted":True}
        return self._write(owner,"session",body,action)

    def attempt(self,owner:str,body:AttemptBody)->dict:
        feedback=_assessment(body.case_id,body.variant,body.answers)
        def action(db,data):
            exposed=db.execute("SELECT 1 FROM interview_events WHERE owner_id=? AND case_id=? AND variant=? AND kind IN ('attempt','reveal') LIMIT 1",
                               (owner,body.case_id,body.variant)).fetchone()
            primary_exists=db.execute("SELECT 1 FROM interview_events WHERE owner_id=? AND case_id=? AND variant='primary' AND kind='attempt' LIMIT 1",
                                      (owner,body.case_id)).fetchone()
            independent=not bool(exposed) and (body.variant=="primary" or bool(primary_exists))
            value={"id":"iat_"+uuid.uuid4().hex,"case_id":body.case_id,"variant":body.variant,
                   "schema_version":SCHEMA,"task_snapshot":case_task(body.case_id,body.variant),
                   "answers":body.answers,"reasoning":body.reasoning,"created_at":_stamp(),"persisted":True,
                   "independent":independent,"independence_note": "First attempt with no correction exposure recorded on this account; not proctored." if independent else "Practice only: correction/prior attempt seen, or transfer attempted before the primary case.",
                   "numerical_pass":feedback["numerical_pass"],"reasoning_reviewed":False,
                   "feedback":{**feedback,"independent":independent}}
            db.execute("UPDATE interview_profiles SET current_task=?,updated_at=? WHERE owner_id=?",
                       (_json({"case_id":body.case_id,"variant":body.variant}),_stamp(),owner))
            return value
        return self._write(owner,"attempt",body,action)

    def reveal(self,owner:str,body:TaskBody)->dict:
        def action(db,data):
            return {"id":"rev_"+uuid.uuid4().hex,"case_id":body.case_id,"variant":body.variant,
                    "created_at":_stamp(),"independent":False,"persisted":True,
                    "notice":"Reference revealed. A later attempt on this exact task is practice only.",
                    "feedback":_assessment(body.case_id,body.variant)}
        return self._write(owner,"reveal",body,action)

    def review(self,owner:str,attempt_id:str,body:ReviewBody)->dict:
        def action(db,data):
            attempt=db.execute("SELECT * FROM interview_events WHERE owner_id=? AND id=? AND kind='attempt'",(owner,attempt_id)).fetchone()
            if not attempt:
                raise HTTPException(status_code=404,detail="Attempt not found.")
            return {"id":"irv_"+uuid.uuid4().hex,"attempt_id":attempt_id,"created_at":_stamp(),
                    "criteria":body.criteria.model_dump(),"notes":body.notes,
                    "reasoning_reviewed":True,"all_criteria_self_reported":all(body.criteria.model_dump().values()),
                    "assessment_type":"learner_self_review","notice":"Self-review saved; no expert score or certification is implied."}
        # Bind the URL target into the idempotency fingerprint too.
        return self._write(owner,"review:"+attempt_id,body,action)

    def state(self,owner:str)->dict:
        with self._connect() as db:
            self._ensure(db,owner)
            profile=db.execute("SELECT * FROM interview_profiles WHERE owner_id=?",(owner,)).fetchone()
            rows=db.execute("SELECT * FROM interview_events WHERE owner_id=? ORDER BY rowid",(owner,)).fetchall()
        attempts=[json.loads(row["payload"]) for row in rows if row["kind"]=="attempt"]
        reviews=[json.loads(row["payload"]) for row in rows if row["kind"].startswith("review:")]
        exposures=[{key:json.loads(row["payload"])[key] for key in ("case_id","variant","created_at")} for row in rows if row["kind"]=="reveal"]
        latest_reviews={r["attempt_id"]:r for r in reviews}
        for attempt in attempts:
            review=latest_reviews.get(attempt["id"])
            attempt["reasoning_reviewed"]=review is not None
            attempt["self_review"]=review
        checked={(a["case_id"],a["variant"]) for a in attempts if a["independent"] and a["numerical_pass"]}
        attempted={(a["case_id"],a["variant"]) for a in attempts}
        next_task=next(({"case_id":cid,"variant":v} for cid in CASE_IDS for v in ("primary","transfer") if (cid,v) not in attempted),None)
        metrics={"attempted_cases":len({a["case_id"] for a in attempts}),"attempt_count":len(attempts),
                 "numerical_checks_passed":len(checked),"numerical_cases_passed":sum((cid,"primary") in checked for cid in CASE_IDS),
                 "transfer_checks_passed":sum(v=="transfer" for _,v in checked),
                 "reasoning_self_reviewed":len(latest_reviews),"reported_active_seconds":profile["active_seconds"],
                 "total_cases":len(CASE_IDS),"total_tasks":2*len(CASE_IDS),"certified_mastery":False,
                 "active_time_basis":"Client-reported foreground activity capped by elapsed server time; not attendance verification."}
        metrics.update({"cases_attempted":metrics["attempted_cases"],
                        "numerical_passes":metrics["numerical_cases_passed"],
                        "transfer_passes":metrics["transfer_checks_passed"],
                        "reasoning_reviews":metrics["reasoning_self_reviewed"],
                        "active_seconds":metrics["reported_active_seconds"]})
        return {"schema_version":SCHEMA,"owner_id":owner,"onboarding":json.loads(profile["onboarding"]) if profile["onboarding"] else None,
                "current_task":json.loads(profile["current_task"]),"attempts":attempts,"exposures":exposures,
                "metrics":metrics,"next_task":next_task,"created_at":profile["created_at"],"updated_at":profile["updated_at"],
                "limitations":LIMITATIONS}

    def pilot_metrics(self,environment:str)->dict:
        """Aggregate participation without selecting answer text or identifiers.

        Read all counters in one SQLite snapshot. Distinct-account counts refer
        only to this database, including any test accounts stored there.
        """
        with self._connect() as db:
            db.execute("BEGIN")
            learners=db.execute("SELECT COUNT(*) FROM interview_profiles").fetchone()[0]
            active_seconds=db.execute("SELECT COALESCE(SUM(active_seconds),0) FROM interview_profiles").fetchone()[0]
            general=db.execute("""
                SELECT COUNT(DISTINCT CASE WHEN variant='primary' THEN owner_id END) AS activated,
                       COUNT(DISTINCT CASE WHEN variant='transfer' THEN owner_id END) AS transfer_attempted,
                       COUNT(DISTINCT CASE WHEN variant='transfer' AND json_extract(payload,'$.independent')=1
                           AND json_extract(payload,'$.numerical_pass')=1 THEN owner_id END) AS transfer_passed,
                       COUNT(*) AS attempts,
                       COALESCE(SUM(variant='primary'),0) AS primary_attempts,
                       COALESCE(SUM(variant='transfer'),0) AS transfer_attempts,
                       COALESCE(SUM(variant='primary' AND json_extract(payload,'$.independent')=1
                           AND json_extract(payload,'$.numerical_pass')=1),0) AS primary_passes,
                       COALESCE(SUM(variant='transfer' AND json_extract(payload,'$.independent')=1
                           AND json_extract(payload,'$.numerical_pass')=1),0) AS transfer_passes
                FROM interview_events WHERE kind='attempt'
            """).fetchone()
            returned=db.execute("""
                SELECT COUNT(*) FROM (
                    SELECT owner_id FROM interview_events WHERE kind='attempt'
                    GROUP BY owner_id HAVING COUNT(DISTINCT substr(created_at,1,10)) >= 2
                )
            """).fetchone()[0]
            reviewed=db.execute("""
                SELECT COUNT(DISTINCT json_extract(payload,'$.attempt_id'))
                FROM interview_events WHERE kind LIKE 'review:%'
            """).fetchone()[0]
            by_case=db.execute("""
                SELECT case_id, COUNT(DISTINCT owner_id) AS learners_attempted,
                       COUNT(DISTINCT CASE WHEN variant='primary' AND json_extract(payload,'$.independent')=1
                           AND json_extract(payload,'$.numerical_pass')=1 THEN owner_id END) AS first_attempts_passed,
                       COUNT(DISTINCT CASE WHEN variant='transfer' THEN owner_id END) AS transfer_attempted,
                       COUNT(DISTINCT CASE WHEN variant='transfer' AND json_extract(payload,'$.independent')=1
                           AND json_extract(payload,'$.numerical_pass')=1 THEN owner_id END) AS transfer_passed
                FROM interview_events WHERE kind='attempt' GROUP BY case_id
            """).fetchall()
        lookup={row["case_id"]:dict(row) for row in by_case}
        per_case=[lookup.get(cid,{"case_id":cid,"learners_attempted":0,"first_attempts_passed":0,
                                  "transfer_attempted":0,"transfer_passed":0}) for cid in CASE_IDS]
        return {"schema_version":SCHEMA,"environment":environment,"generated_at":_stamp(),
                "scope_notice":("Local/test activity in this database only. " if environment != "production" else "Participation in this database only, including any test accounts. ")+
                    "These are not customer, payment, sales-conversion or product-market-fit counts.",
                "learners_seen":learners,"activated_learners":general["activated"],
                "transfer_attempted_learners":general["transfer_attempted"],
                "transfer_passed_learners":general["transfer_passed"],"returned_on_later_day":returned,
                "per_case":per_case,
                "totals":{"attempts":general["attempts"],"primary_attempts":general["primary_attempts"],
                          "transfer_attempts":general["transfer_attempts"],"independent_primary_passes":general["primary_passes"],
                          "independent_transfer_passes":general["transfer_passes"],"reasoning_self_reviews":reviewed,
                          "reported_active_seconds":active_seconds},
                "definitions":{"learners_seen":"Distinct account profiles created by opening saved state or making a saved action; not anonymous visitors.",
                               "activated_learners":"Distinct accounts with at least one primary-case attempt.",
                               "returned_on_later_day":"Distinct accounts with attempts on at least two UTC calendar dates; not a D7 retention cohort.",
                               "first_attempts_passed":"Distinct accounts with a primary numerical pass and no previous exposure recorded for that task.",
                               "transfer_passed":"Distinct accounts with a transfer numerical pass and no previous exposure recorded for that task, after a primary attempt.",
                               "reasoning_self_reviews":"Distinct attempts with a submitted learner rubric; not expert-graded memos."},
                "limitations":LIMITATIONS}


def register_interview_routes(app:FastAPI,db_path:Path,security:ApiSecurity)->None:
    store=InterviewLabStore(db_path)

    def identity(request:Request)->AuthenticatedIdentity:
        signed=getattr(request.state,"tpl_identity",None)
        if not isinstance(signed,AuthenticatedIdentity):
            security.authorize(request,IDENTITY)
            signed=getattr(request.state,"tpl_identity",None)
        if not isinstance(signed,AuthenticatedIdentity):
            raise HTTPException(status_code=401,detail="A verified signed learner session is required to save interview practice.")
        return signed

    def private(response:Response)->None:
        response.headers["Cache-Control"]="private, no-store"
        response.headers["Vary"]="Authorization"

    @app.get("/interview/catalog")
    def interview_catalog()->dict:
        return catalogue()

    @app.get("/interview/pilot/metrics")
    def interview_pilot_metrics(request:Request,response:Response)->dict:
        # Middleware is authoritative; this explicit check also rejects relaxed
        # local fallback and shared member keys if a handler is reused directly.
        signed=getattr(request.state,"tpl_identity",None)
        signed_operator=isinstance(signed,AuthenticatedIdentity) and signed.role==OPERATOR
        trusted_operator=security._role_for_key(security._presented_key(request))==OPERATOR
        if not signed_operator and not trusted_operator:
            raise HTTPException(status_code=403,detail="Verified operator access is required for pilot aggregates.")
        private(response)
        return store.pilot_metrics(security.settings.environment)

    @app.get("/interview/cases/{case_id}")
    def interview_case(case_id:str,request:Request,response:Response,variant:Variant="primary")->dict:
        if case_id != CASE_IDS[0]:
            identity(request)
            private(response)
        return case_task(case_id,variant)

    @app.post("/interview/preview/check")
    def interview_preview(body:AttemptBody,response:Response)->dict:
        if body.case_id != CASE_IDS[0]:
            raise HTTPException(status_code=403,detail="Only the first case is available in the public preview. Sign in for the full pilot.")
        private(response)
        feedback=_assessment(body.case_id,body.variant,body.answers)
        return {"attempt":{"id":None,"case_id":body.case_id,"variant":body.variant,"answers":body.answers,"reasoning":body.reasoning,
                "schema_version":SCHEMA,"task_snapshot":case_task(body.case_id,body.variant),
                "numerical_pass":feedback["numerical_pass"],"independent":False,"persisted":False,
                "reasoning_reviewed":False,"created_at":_stamp(),"feedback":{**feedback,"independent":False},
                "notice":"Unsaved public preview. Sign in to preserve attempts and independent transfer checks."}}

    @app.get("/interview/state")
    def interview_state(request:Request,response:Response)->dict:
        private(response)
        return store.state(identity(request).user_id)

    @app.post("/interview/onboarding")
    def interview_onboarding(body:OnboardingBody,request:Request,response:Response)->dict:
        private(response)
        return {"onboarding":store.onboarding(identity(request).user_id,body)}

    @app.post("/interview/session")
    def interview_session(body:SessionBody,request:Request,response:Response)->dict:
        private(response)
        return store.session(identity(request).user_id,body)

    @app.post("/interview/attempts")
    def interview_attempt(body:AttemptBody,request:Request,response:Response)->dict:
        private(response)
        return {"attempt":store.attempt(identity(request).user_id,body)}

    @app.post("/interview/reveal")
    def interview_reveal(body:TaskBody,request:Request,response:Response)->dict:
        private(response)
        return store.reveal(identity(request).user_id,body)

    @app.post("/interview/attempts/{attempt_id}/review")
    def interview_review(attempt_id:str,body:ReviewBody,request:Request,response:Response)->dict:
        private(response)
        if len(attempt_id)>100:
            raise HTTPException(status_code=404,detail="Attempt not found.")
        return {"review":store.review(identity(request).user_id,attempt_id,body)}

    @app.get("/interview/export")
    def interview_export(request:Request,response:Response)->dict:
        private(response)
        response.headers["Content-Disposition"]='attachment; filename="tpl-interview-practice.json"'
        return {**store.state(identity(request).user_id),"exported_at":_stamp(),"report_type":"Personal practice record; not a qualification certificate"}
