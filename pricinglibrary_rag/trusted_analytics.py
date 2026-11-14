"""Strict, offline numerical adapters shared by registered tools and RFQs.

Rates/volatility are decimals, time is ACT/365F years. The autocall is an
original single-asset, discrete-observation GBM teaching model, not LSV or a
calibrated market model. No provider, broker or private corpus is used.
"""
from __future__ import annotations

import math
import re
from typing import Any

import numpy as np

from .black_scholes import BLACK_SCHOLES_INPUT_SCHEMA, analyze_black_scholes

VERSION = "tpl.trusted-analytics.v1"


def number(value: Any, name: str, low: float, high: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number.")
    value=float(value)
    if not low <= value <= high:raise ValueError(f"{name} must be within [{low}, {high}].")
    return value


def _finite_tree(value:Any)->None:
    if isinstance(value,float) and not math.isfinite(value):raise ValueError('Every numeric ticket field must be finite, including optional fields.')
    if isinstance(value,dict):
        for item in value.values():_finite_tree(item)
    elif isinstance(value,(list,tuple)):
        for item in value:_finite_tree(item)


def parse_ticket(text: str) -> dict:
    """Extract only explicitly named numbers, never replace an existing ticket."""
    text=text or "";out={}
    patterns={
        "spot":r"\b(?:spot|S)\s*(?:=|:)?\s*([-+]?\d+(?:\.\d+)?)",
        "forward":r"\b(?:forward|F)\s*(?:=|:)?\s*([-+]?\d+(?:\.\d+)?)",
        "strike":r"\b(?:strike|K)\s*(?:=|:)?\s*([-+]?\d+(?:\.\d+)?)",
        "riskFreeRate":r"\b(?:risk[- ]free(?: rate)?|rate|r)\s*(?:=|:)?\s*([-+]?\d+(?:\.\d+)?)\s*(%)?",
        "dividendYield":r"\b(?:dividend(?: yield)?|foreign(?: rate)?|q)\s*(?:=|:)?\s*([-+]?\d+(?:\.\d+)?)\s*(%)?",
        "volatility":r"\b(?:volatility|sigma|vol|σ)\s*(?:=|:)?\s*([-+]?\d+(?:\.\d+)?)\s*(%)?",
        "maturityYears":r"\b(?:maturity(?: years)?|T)\s*(?:=|:)?\s*(\d+(?:\.\d+)?)\s*(years?|ans?|months?|mois|days?|jours?)?",
        "notional":r"\bnotional\s*(?:=|:)?\s*(\d+(?:\.\d+)?)\s*(billion|million|thousand|bn|[kmb])?\b",
        "quantity":r"\b(?:quantity|qty)\s*(?:=|:)?\s*(\d+(?:\.\d+)?)\s*(billion|million|thousand|bn|[kmb])?\b",
        "riskLimit":r"\b(?:risk[-_ ]limit|limit)\s*(?:=|:)?\s*(\d+(?:\.\d+)?)",
    }
    for key,pattern in patterns.items():
        m=re.search(pattern,text,re.I)
        if not m:continue
        value=float(m.group(1))
        if key in {"riskFreeRate","dividendYield","volatility"} and m.group(2):value/=100
        if key in {"notional","quantity"}:
            value*={"k":1e3,"thousand":1e3,"m":1e6,"million":1e6,"b":1e9,"bn":1e9,"billion":1e9}.get((m.group(2) or "").lower(),1)
        if key=="maturityYears":
            unit=(m.group(2) or "").lower()
            if unit.startswith(("month","mois")):value/=12
            elif unit.startswith(("day","jour")):value/=365
        out[key]=value
    if "maturityYears" not in out:
        m=re.search(r"\b(\d+(?:\.\d+)?)\s*(years?|ans?|months?|mois)\b",text,re.I)
        if m:out["maturityYears"]=float(m.group(1))/(12 if m.group(2).lower().startswith(("month","mois")) else 1)
    if re.search(r"\bput\b",text,re.I):out["optionType"]="put"
    elif re.search(r"\bcall\b",text,re.I):out["optionType"]="call"
    return out


def normalise_ticket(payload:dict, *, defaults:dict|None=None, model:str="bsm") -> dict:
    if not isinstance(payload,dict):raise ValueError("A ticket object is required.")
    _finite_tree(payload)
    data={**(defaults or {}),**parse_ticket(str(payload.get("query") or ""))}
    aliases={"S":"spot","K":"strike","T":"maturityYears","maturity":"maturityYears","rate":"riskFreeRate",
             "r":"riskFreeRate","q":"dividendYield","sigma":"volatility","option_type":"optionType",
             "foreignRate":"dividendYield","domesticRate":"riskFreeRate"}
    for key,value in payload.items():
        if key not in {"query","confirmed"}:data[aliases.get(key,key)]=value
    if model=="black76":
        explicit=parse_ticket(str(payload.get("query") or ""))
        if "forward" not in payload and "forward" not in explicit and ("spot" in payload or "S" in payload or "spot" in explicit):
            data["forward"]=data["spot"]
        if "forward" not in data and "spot" in data:data["forward"]=data["spot"]
        if "forward" in data:data["spot"]=data["forward"]
    missing=[k for k in ("spot","strike","maturityYears","riskFreeRate","volatility") if k not in data]
    if missing:raise ValueError("Missing explicit ticket inputs: "+", ".join(missing))
    for key,low,high in [("spot",1e-8,1e9),("strike",1e-8,1e9),("maturityYears",0,30),
                         ("riskFreeRate",-1,1),("dividendYield",-1,1),("volatility",0,5)]:
        data[key]=number(data.get(key,0 if key=="dividendYield" else None),key,low,high)
    data.setdefault("optionType","call")
    if data["optionType"] not in {"call","put"}:raise ValueError("optionType must be call or put.")
    data.setdefault("currency","USD")
    for key in ('quantity','notional'):
        if key in data:data[key]=number(data[key],key,1e-8,1e15)
    return data


def option_analysis(payload:dict, *, model:str="bsm", defaults:dict|None=None) -> dict:
    ticket=normalise_ticket(payload,defaults=defaults,model=model)
    q=ticket["riskFreeRate"] if model=="black76" else ticket["dividendYield"]
    raw={"schemaVersion":BLACK_SCHOLES_INPUT_SCHEMA,"quoteMode":"volatility","optionType":ticket["optionType"],
         "spot":ticket["spot"],"strike":ticket["strike"],"maturityYears":ticket["maturityYears"],"dayCount":"ACT/365F",
         "riskFreeRate":ticket["riskFreeRate"],"dividendYield":q,"volatility":ticket["volatility"],"marketPrice":None,
         "currency":ticket["currency"],"position":"long","quantity":1,"multiplier":1,
         "shocks":{"spotPct":5,"volPoints":1,"days":1}}
    result=analyze_black_scholes(raw);selected=result["selected"]
    greeks=dict(selected["greeks"])
    if model=="black76":greeks["rho"]=-ticket["maturityYears"]*selected["unitPrice"]/100
    model_name={"bsm":"Black-Scholes-Merton European","black76":"Black-76 European forward option","gk":"Garman-Kohlhagen European FX option"}[model]
    return {"schemaVersion":VERSION,"model":model_name,"engineVersion":result["engineVersion"],"analysisId":result["analysisId"],
            "value":selected["unitPrice"],"unit":ticket["currency"]+" per underlying unit","greeks":greeks,
            "inputs":ticket,"parity":result["parity"],"call":result["call"]["unitPrice"],"put":result["put"]["unitPrice"],
            "conventions":{"rates":"continuous annual decimals","time":"ACT/365F years","vega":"per +1 volatility percentage point",
                           "theta":"per calendar day","rho":"per +1 rate percentage point",
                           "underlying":"forward held fixed; q=r adapter; rho discounts only" if model=="black76" else "spot with continuous dividend/foreign yield"},
            "limitations":["Flat volatility and deterministic continuous rates/carry; European exercise.","Educational model value, not an executable quote or calibrated smile."]}


def swap_analysis(payload:dict)->dict:
    """Single-flat-curve payer/receiver swap, annual payments plus final stub."""
    _finite_tree(payload)
    n=number(payload.get("notional",1e6),"notional",1,1e12);t=number(payload.get("maturityYears",5),"maturityYears",1e-6,30)
    r=number(payload.get("riskFreeRate",.04),"riskFreeRate",-.2,.5)
    dates=list(range(1,int(math.floor(t))+1))
    if not dates or dates[-1]<t:dates.append(t)
    def terms(rate):
        ann=sum((time-(dates[i-1] if i else 0))*math.exp(-rate*time) for i,time in enumerate(dates))
        return ann,(1-math.exp(-rate*t))/ann
    ann,par=terms(r);fixed=number(payload.get("fixedRate",par),"fixedRate",-.2,.5)
    if payload.get('direction','payer') not in {'payer','receiver'}:raise ValueError('direction must be payer or receiver.')
    sign=-1 if payload.get("direction")=="receiver" else 1
    def value(rate):
        a,p=terms(rate);return sign*n*a*(p-fixed)
    pv=value(r);dv01=(value(r+.0001)-value(r-.0001))/2
    return {"model":"Single-flat-curve discounted swap cash flows","value":pv,"unit":payload.get("currency","USD"),
            "greeks":{"dv01":dv01},"annuity":ann,"parRate":par,
            "inputs":{"notional":n,"maturityYears":t,"riskFreeRate":r,"fixedRate":fixed,"direction":"receiver" if sign<0 else "payer","currency":payload.get("currency","USD")},
            "limitations":["Illustrative flat continuous-yield curve; annual fixed payments and final stub. No external bootstrap or multi-curve calibration."]}


def cds_analysis(payload:dict)->dict:
    """Flat-hazard CDS approximation with a continuously paid fixed coupon."""
    _finite_tree(payload)
    n=number(payload.get("notional",1e6),"notional",1,1e12);t=number(payload.get("maturityYears",5),"maturityYears",1e-6,30)
    r=number(payload.get("riskFreeRate",.03),"riskFreeRate",-.2,.5)
    spread=number(payload.get("spread",.012),"spread",1e-6,1)
    coupon=number(payload.get("coupon",spread),"coupon",0,1);recovery=number(payload.get("recovery",.4),"recovery",0,.99)
    def value(s):
        hazard=s/(1-recovery);discount=r+hazard
        ann=t if abs(discount)<1e-12 else -math.expm1(-discount*t)/discount
        return n*ann*(s-coupon),ann
    pv,ann=value(spread);bump=min(.0001,spread*.25)
    cs01=(value(spread+bump)[0]-value(spread-bump)[0])/(2*bump)*.0001
    return {"model":"Flat-hazard continuous-premium CDS approximation","value":pv,"unit":payload.get("currency","EUR"),
            "greeks":{"cs01":cs01},"risky_annuity":ann,"running_spread":spread,"jump_to_default":n*(1-recovery),
            "inputs":{"notional":n,"maturityYears":t,"riskFreeRate":r,"spread":spread,"coupon":coupon,"recovery":recovery,"currency":payload.get("currency","EUR")},
            "limitations":["Flat hazard = supplied par spread / (1-recovery); continuous premium approximation. No market hazard-curve calibration or accrued-on-default convention."]}


def autocall_analysis(payload:dict, *, sensitivities:bool=True) -> dict:
    """Seeded GBM autocall with memory coupons and terminal capital protection."""
    defaults={"spot":100.0,"referenceSpot":100.0,"riskFreeRate":0.03,"dividendYield":0.01,"volatility":0.22,
              "maturityYears":3.0,"couponRate":0.06,"observationsPerYear":4,"autocallBarrier":1.0,
              "couponBarrier":0.7,"protectionBarrier":0.6,"paths":8192,"seed":17,"notional":1_000_000,"currency":"EUR"}
    if not isinstance(payload,dict):raise ValueError("An autocall ticket object is required.")
    _finite_tree(payload)
    data={**defaults,**parse_ticket(str(payload.get("query") or "")),**payload}
    if not isinstance(data['currency'],str) or not re.fullmatch('[A-Z]{3}',data['currency']):raise ValueError('currency must be an uppercase three-letter currency code.')
    if "spot" in payload and "referenceSpot" not in payload:data["referenceSpot"]=payload["spot"]
    limits={"spot":(1e-6,1e8),"referenceSpot":(1e-6,1e8),"riskFreeRate":(-.2,.5),"dividendYield":(-.2,.5),
            "volatility":(0,2),"maturityYears":(.25,10),"couponRate":(0,1),"autocallBarrier":(.1,3),
            "couponBarrier":(.05,3),"protectionBarrier":(.05,1),"notional":(1,1e10)}
    for key,(low,high) in limits.items():data[key]=number(data[key],key,low,high)
    for key,low,high in [("paths",256,20000),("seed",0,2**32-1),("observationsPerYear",1,12)]:
        if isinstance(data[key],bool) or not isinstance(data[key],int) or not low<=data[key]<=high:raise ValueError(f"{key} must be an integer within [{low}, {high}].")
    if data["couponBarrier"]>data["autocallBarrier"]:raise ValueError("couponBarrier must not exceed autocallBarrier in this supported memory-coupon contract.")
    regular=int(math.floor(data["maturityYears"]*data["observationsPerYear"]+1e-12))
    dates=[j/data["observationsPerYear"] for j in range(1,regular+1)]
    if not dates or dates[-1]<data["maturityYears"]-1e-12:dates.append(data["maturityYears"])
    steps=len(dates)
    if steps>120:raise ValueError("At most 120 observation dates are supported.")
    n=data["paths"]
    if n%2:raise ValueError("paths must be even for antithetic pair estimation.")
    half=n//2
    z=np.random.default_rng(data["seed"]).standard_normal((steps,half))
    shocks=np.concatenate((z,-z),axis=1)
    def simulate(spot,vol):
        ratios=np.full(n,spot/data["referenceSpot"],dtype=float);pv=np.zeros(n);alive=np.ones(n,dtype=bool);memory=np.zeros(n)
        called=np.zeros(n,dtype=bool)
        for j in range(steps):
            dt=dates[j]-(dates[j-1] if j else 0)
            ratios*=np.exp((data["riskFreeRate"]-data["dividendYield"]-.5*vol*vol)*dt+vol*math.sqrt(dt)*shocks[j])
            memory[alive]+=data["couponRate"]*dt
            coupon=alive&(ratios>=data["couponBarrier"])
            discount=math.exp(-data["riskFreeRate"]*dates[j])
            pv[coupon]+=memory[coupon]*discount;memory[coupon]=0
            call=alive&(ratios>=data["autocallBarrier"])
            pv[call]+=discount;alive[call]=False;called[call]=True
        redemption=np.where(ratios>=data["protectionBarrier"],1.0,ratios)
        pv[alive]+=redemption[alive]*math.exp(-data["riskFreeRate"]*data["maturityYears"])
        return pv,called
    values,called=simulate(data["spot"],data["volatility"])
    def paired_error(samples):
        pairs=(samples[:half]+samples[half:])/2
        return float(pairs.std(ddof=1)/math.sqrt(half))
    mean=float(values.mean());se=paired_error(values)
    greeks={"delta":None,"gamma":None,"vega":None,"correlation":None}
    greek_errors={"delta":None,"gamma":None,"vega":None,"correlation":None}
    if sensitivities:
        h=max(.01,data["spot"]*.01);h=min(h,data["spot"]*.25)
        ups=simulate(data["spot"]+h,data["volatility"])[0];downs=simulate(data["spot"]-h,data["volatility"])[0]
        vh=min(.01,max(.0001,data["volatility"]*.25));vlow=max(0,data["volatility"]-vh);vhigh=data["volatility"]+vh
        vus=simulate(data["spot"],vhigh)[0];vds=simulate(data["spot"],vlow)[0]
        samples={"delta":(ups-downs)/(2*h)*data["notional"],
                 "gamma":(ups-2*values+downs)/(h*h)*data["notional"],
                 "vega":(vus-vds)/(vhigh-vlow)*.01*data["notional"]}
        for key,sample in samples.items():greeks[key]=float(sample.mean());greek_errors[key]=paired_error(sample)
    return {"schemaVersion":VERSION,"model":"Single-asset risk-neutral GBM Monte Carlo, discrete observations",
            "inputs":data,"engineVersion":"autocall-gbm-v1","value":mean*100,"unit":"percent of par",
            "present_value":mean*data["notional"],"standard_error_percent_par":se*100,
            "confidence_interval_95_percent_par":[(mean-1.96*se)*100,(mean+1.96*se)*100],
            "paths":n,"observation_count":steps,"seed":data["seed"],"autocall_frequency_in_simulation":float(called.mean()),
            "observation_times_years":dates,
            "greeks":greeks,"greek_standard_errors":greek_errors,"independent_antithetic_pairs":half,
            "standard_error_method":"Sample standard deviation of antithetic pair averages divided by sqrt(independent pair count).",
            "sensitivity_method":"Common-random-number central finite differences; delta/gamma per spot unit, vega per +1 volatility percentage point, scaled to notional; paired Monte Carlo standard errors are reported.",
            "limitations":["Original educational single-asset constant-volatility GBM model; no LSV, calibrated smile, correlation model or live market data.",
                            "Discrete coupon/autocall observations; capital protection tested only at maturity; no issuer credit/funding spread.",
                            "Barrier finite-difference sensitivities and confidence intervals contain Monte Carlo sampling error; not a hedge recommendation.",
                            "Correlation sensitivity is unavailable for a single-asset model."]}
