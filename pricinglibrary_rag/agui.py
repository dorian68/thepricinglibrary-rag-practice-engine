"""AG-UI (Agent-User Interaction Protocol) streaming endpoint.

This module turns the existing RAG + calculator + generation services into an
agentic, page-aware educational assistant streamed over SSE to the React
frontend. It implements the AG-UI event families described in
``AG_UI_IMPLEMENTATION_GUIDE.md``:

    RunStarted -> StateSnapshot -> (ToolCall* / Custom app.*) -> TextMessage* -> RunFinished

Two runtimes are provided and share the same tool executors:

* ``_run_openai_agent`` — real OpenAI function-calling loop (default model
  ``gpt-4o-mini``) with token streaming. Used when provider==openai and a key
  is configured.
* ``_run_offline_agent`` — deterministic, intent-based fallback that still uses
  the *real* local retriever and calculators (no LLM cost). Used for
  provider==template / missing key, so the whole experience works offline.

Nothing here mutates application data, so no human-in-the-loop approval gate is
required for the shipped tools (rag_search / pricing / tool-param control /
exercise generation are all read-only or client-side UI hints). The approval
event contract is still defined so sensitive tools can be added later.
"""

import json
import math
import os
import time
import uuid
from typing import Any, Callable, Iterable, Iterator

from .factory import Services
from .black_scholes import BLACK_SCHOLES_INPUT_SCHEMA, analyze_black_scholes
from .binomial import BINOMIAL_INPUT_SCHEMA, analyze_binomial
from .bond import BOND_INPUT_SCHEMA, analyze_bond
from .vol_surface import INPUT_SCHEMA as VOL_SURFACE_INPUT_SCHEMA, analyze_vol_surface
from .monte_carlo import INPUT_SCHEMA_VERSION as MONTE_CARLO_INPUT_SCHEMA, MonteCarloError, run_monte_carlo
from .schemas import ExerciseRequest, SearchRequest

# ---------------------------------------------------------------------------
# UIBlock allowlist — the frontend renders ONLY these component types.
# ---------------------------------------------------------------------------
ALLOWED_UI_BLOCKS = {
    # generic
    "summary_card",
    "action_card",
    "confirmation_card",
    "metric_grid",
    "data_table",
    "chart_block",
    "form_block",
    "suggestion_chips",
    "progress_steps",
    "error_card",
    "calculation_steps",
    # RAG
    "source_card",
    "rag_source_block",
    # quant finance
    "latex_formula_block",
    "derivation_steps_block",
    "payoff_chart_block",
    "payoff_block",
    "black_scholes_explorer_block",
    "bs_pricer_block",
    "greeks_sensitivity_block",
    "put_call_parity_block",
    "monte_carlo_simulation_block",
    "binomial_tree_block",
    "structured_product_payoff_block",
    # learning
    "exercise_block",
    "quiz_block",
    "answer_feedback_block",
    "concept_map_block",
}

# Tools the agent may drive on the frontend (client-side, non-sensitive).
KNOWN_TOOLS = {"bs-pricer", "payoff", "mc", "iv-calc", "calib", "binomial", "bond", "curve", "volsurface"}


def _env_int(name: str, default: int) -> int:
    try:
        return max(1, int(os.environ.get(name, default)))
    except (TypeError, ValueError):
        return default


# --- Cost guardrails (configurable via env) --------------------------------
# Per-call output cap, per-run total-token budget, max tool/think iterations,
# and how many prior messages we forward. Defaults are tuned for a cheap
# gpt-4o-mini chat assistant; raise them deliberately if needed.
MAX_AGENT_STEPS = _env_int("AG_UI_MAX_STEPS", 5)
MAX_OUTPUT_TOKENS = _env_int("AG_UI_MAX_OUTPUT_TOKENS", 900)
MAX_TOTAL_TOKENS = _env_int("AG_UI_MAX_TOTAL_TOKENS", 6000)
MAX_HISTORY_MESSAGES = _env_int("AG_UI_MAX_HISTORY", 12)


# ---------------------------------------------------------------------------
# SSE helpers + event factories
# ---------------------------------------------------------------------------
def _sse(event: dict) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


def _now() -> str:
    # Wall-clock timestamp for observability only (not used for logic).
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + "Z"


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


# ---------------------------------------------------------------------------
# Black-Scholes AG-UI compatibility adapter. Human inputs retain the historical
# percent/day units, but every result delegates to the strict F-CAL10 engine.
# ---------------------------------------------------------------------------
def _canonical_bs_input(S: Any, K: Any, r: Any, q: Any, sigma: Any, T_days: Any, option_type: str = "call") -> dict:
    return {
        "schemaVersion": BLACK_SCHOLES_INPUT_SCHEMA,
        "quoteMode": "volatility", "optionType": option_type,
        "spot": S, "strike": K, "maturityYears": T_days / 365.0 if type(T_days) in (int, float) and not isinstance(T_days, bool) else T_days,
        "dayCount": "ACT/365F",
        "riskFreeRate": r / 100.0 if type(r) in (int, float) and not isinstance(r, bool) else r,
        "dividendYield": q / 100.0 if type(q) in (int, float) and not isinstance(q, bool) else q,
        "volatility": sigma / 100.0 if type(sigma) in (int, float) and not isinstance(sigma, bool) else sigma,
        "marketPrice": None, "currency": "EUR", "position": "long", "quantity": 1.0, "multiplier": 1.0,
        "shocks": {"spotPct": 10.0, "volPoints": 5.0, "days": 30.0},
    }


def _legacy_bs(result: dict) -> dict:
    call, put = result["call"], result["put"]
    return {
        "call": call["unitPrice"], "put": put["unitPrice"],
        "delta_call": call["greeks"]["delta"], "delta_put": put["greeks"]["delta"],
        "gamma": call["greeks"]["gamma"], "vega": call["greeks"]["vega"],
        "theta_call": call["greeks"]["theta"], "theta_put": put["greeks"]["theta"],
        "rho_call": call["greeks"]["rho"], "rho_put": put["greeks"]["rho"],
        "parity_lhs": result["parity"]["lhs"], "parity_rhs": result["parity"]["rhs"],
        "parity_holds": result["parity"]["holds"],
        "degenerate": call["limit"] != "closed_form",
        "analysis_id": result["analysisId"], "engine_version": result["engineVersion"],
        "units": result["conventions"],
    }


def black_scholes(S: float, K: float, r: float, q: float, sigma: float, T_days: float) -> dict:
    return _legacy_bs(analyze_black_scholes(_canonical_bs_input(S, K, r, q, sigma, T_days)))


def bs_full(S: float, K: float, r: float, q: float, sigma: float, T_days: float) -> dict:
    return black_scholes(S, K, r, q, sigma, T_days)


def greeks_sensitivity(greek: str, param: str, base: dict, points: int = 21) -> dict:
    if greek not in ("delta", "gamma", "vega", "theta", "rho", "call", "put"):
        raise ValueError("greek is unsupported.")
    if param not in ("spot", "vol", "time", "strike"):
        raise ValueError("param is unsupported.")
    if points != 21:
        raise ValueError("points must equal the canonical sensitivity count 21.")
    canonical = _canonical_bs_input(base["S"], base["K"], base["r"], base["q"], base["sigma"], base["T"])
    initial = analyze_black_scholes(canonical)
    if param == "spot":
        xs = [row["x"] for row in initial["sensitivities"]["spot"]]
    elif param == "vol":
        xs = [row["x"] * 100.0 for row in initial["sensitivities"]["volatility"]]
    elif param == "time":
        xs = [row["x"] * 365.0 for row in initial["sensitivities"]["maturity"]]
    else:
        xs = [base["K"] * (0.6 + 0.8 * index / (points - 1)) for index in range(points)]
    series = []
    for x in xs:
        changed = dict(base)
        changed[{"spot": "S", "vol": "sigma", "time": "T", "strike": "K"}[param]] = x
        row = analyze_black_scholes(_canonical_bs_input(changed["S"], changed["K"], changed["r"], changed["q"], changed["sigma"], changed["T"]))
        selected = row["call"] if greek not in ("put",) else row["put"]
        y = selected["unitPrice"] if greek in ("call", "put") else selected["greeks"][greek]
        series.append({"x": x, "y": y})
    return {"greek": greek, "param": param, "series": series, "engineVersion": initial["engineVersion"]}


def mc_simulation(S: float, mu: float, sigma: float, T_days: float, N: int = 400, steps: int = 50, seed: int = 7) -> dict:
    """Compatibility adapter over the canonical F-CAL-6 physical-P engine.

    The AG-UI block keeps its historical presentation keys, but simulation,
    RNG, validation and quantiles all come from ``monte_carlo.py``.  Inputs are
    intentionally not clamped: an invalid request fails closed.
    """
    numeric = {"S": S, "mu": mu, "sigma": sigma, "T": T_days}
    for name, value in numeric.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise MonteCarloError(f"{name} must be a finite JSON number; strings and booleans are rejected.")
    integers = {"N": N, "steps": steps, "seed": seed}
    for name, value in integers.items():
        if isinstance(value, bool) or not isinstance(value, int):
            raise MonteCarloError(f"{name} must be a JSON integer; strings and fractional values are rejected.")
    result = run_monte_carlo({
        "schemaVersion": MONTE_CARLO_INPUT_SCHEMA,
        "mode": "risk_physical",
        "spot": S,
        "volatility": sigma / 100.0,
        "maturityYears": T_days / 365.0,
        "dayCount": "ACT/365F",
        "paths": N,
        "timeSteps": steps,
        "seed": seed,
        "method": "none",
        "samplePaths": min(N, 12),
        "histogramBins": 18,
        "currency": "EUR",
        "quantity": 1,
        "contractMultiplier": 1.0,
        "position": "long",
        "physicalDrift": mu / 100.0,
        "confidence": 0.95,
    })
    quantiles = result["distribution"]["quantiles"]
    return {
        "paths": [[point["spot"] for point in path["points"]] for path in result["samplePaths"]],
        "n": result["run"]["simulatedPaths"],
        "steps": result["run"]["timeSteps"],
        "terminal_mean": result["distribution"]["terminalMean"],
        "p5": quantiles["p05"],
        "p95": quantiles["p95"],
        "histogram": [{"x": row["midpoint"], "count": row["count"]} for row in result["distribution"]["histogram"]],
        "analysis_id": result["analysisId"],
        "engine_version": result["engineVersion"],
        "measure": result["measure"],
        "day_count": result["conventions"]["dayCount"],
    }


def payoff_series(legs: list, lo: float = 50, hi: float = 150, points: int = 80) -> dict:
    """Payoff at expiry vs spot for a list of option legs."""
    net_prem = 0.0
    for l in legs:
        sgn = 1 if l.get("side", "long") == "long" else -1
        net_prem += sgn * float(l.get("prem", 0)) * float(l.get("qty", 1))
    curve = []
    prev_y = None
    breakevens = []
    for i in range(points):
        s = lo + (hi - lo) * i / (points - 1)
        total = 0.0
        for l in legs:
            sgn = 1 if l.get("side", "long") == "long" else -1
            qty = float(l.get("qty", 1))
            K = float(l.get("K", 100))
            intrinsic = max(s - K, 0.0) if l.get("type", "call") == "call" else max(K - s, 0.0)
            total += sgn * qty * intrinsic
        y = total - net_prem
        if prev_y is not None and (prev_y <= 0 < y or prev_y >= 0 > y):
            breakevens.append(round(s, 2))
        prev_y = y
        curve.append({"x": round(s, 2), "y": round(y, 3)})
    ys = [p["y"] for p in curve]
    return {"curve": curve, "breakevens": breakevens, "max_gain": round(max(ys), 3), "max_loss": round(min(ys), 3), "net_premium": round(net_prem, 3)}


def structured_payoff(kind: str, params: dict) -> dict:
    """Simplified terminal payoff of common structured products vs final spot (S0=100)."""
    S0 = 100.0
    barrier = float(params.get("barrier", 60))
    coupon = float(params.get("coupon", 8))
    participation = float(params.get("participation", 100)) / 100.0
    protection = float(params.get("protection", 100)) / 100.0
    curve = []
    for i in range(81):
        st = 40 + i * (160 - 40) / 80.0
        perf = st / S0 - 1.0
        if kind == "capital_protected":
            y = 100 * protection + participation * max(perf, 0.0) * 100
        elif kind == "reverse_convertible":
            y = (100 + coupon) if st >= barrier else (st + coupon)
        elif kind == "autocall":
            y = (100 + coupon) if st >= 100 else (100 if st >= barrier else st)
        elif kind == "barrier_note":
            y = (100 + participation * max(perf, 0.0) * 100) if st >= barrier else st
        else:  # participation
            y = 100 + participation * perf * 100
        curve.append({"x": round(st, 2), "y": round(y, 2)})
    scenarios = {
        "autocall": [
            f"S_T ≥ 100 : remboursement 100 + coupon {coupon}%",
            f"barrière {barrier}% ≤ S_T < 100 : capital protégé (100), pas de coupon",
            f"S_T < {barrier}% : perte en capital, remboursement = S_T (risque de marché)",
        ],
        "capital_protected": [
            f"Capital garanti à {int(protection*100)}% à maturité",
            f"Participation {int(participation*100)}% à la hausse du sous-jacent",
            "Pas de participation à la baisse (coût = renonciation aux dividendes)",
        ],
        "reverse_convertible": [
            f"S_T ≥ barrière {barrier}% : 100 + coupon {coupon}%",
            f"S_T < barrière : livraison/perte, capital = S_T + coupon (coupon élevé = compensation du risque)",
        ],
    }.get(kind, [f"Payoff paramétrique du produit '{kind}'"])
    return {"kind": kind, "curve": curve, "scenarios": scenarios, "barrier": barrier, "coupon": coupon}


def binomial_tree(S: float, K: float, r: float, sigma: float, T_days: float, steps: int, kind: str = "call", american: bool = False, q: float = 0.0) -> dict:
    """Compatibility adapter over the canonical F-CAL-7 CRR engine.

    Historical AG-UI units remain percentages/days. Inputs are not clamped and
    the returned ``steps`` is the requested lattice size; only the rendered node
    preview is bounded to the canonical six-level display contract.
    """
    for name, value in {"S": S, "K": K, "r": r, "q": q, "sigma": sigma, "T": T_days}.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite JSON number; strings and booleans are rejected.")
    if isinstance(steps, bool) or not isinstance(steps, int):
        raise ValueError("steps must be a JSON integer; strings and fractional values are rejected.")
    if kind not in {"call", "put"}:
        raise ValueError("kind must be call or put.")
    if not isinstance(american, bool):
        raise ValueError("american must be a JSON boolean.")
    result = analyze_binomial({
        "schemaVersion": BINOMIAL_INPUT_SCHEMA, "spot": S, "strike": K,
        "volatility": sigma / 100.0, "maturityYears": T_days / 365.0,
        "dayCount": "ACT/365F", "riskFreeRate": r / 100.0,
        "dividendYield": q / 100.0, "steps": steps, "optionType": kind,
        "exerciseStyle": "american" if american else "european",
        "currency": "EUR", "quantity": 1, "contractMultiplier": 1.0,
        "position": "long",
    })
    grouped: dict[int, list[float]] = {}
    for node in result["tree"]["nodes"]:
        grouped.setdefault(node["step"], []).append(round(node["spot"], 2))
    return {
        "price": round(result["valuation"]["pricePerUnit"], 4),
        "u": round(result["model"]["upFactor"], 4),
        "d": round(result["model"]["downFactor"], 4),
        "p": None if result["model"]["riskNeutralUpProbability"] is None else round(result["model"]["riskNeutralUpProbability"], 4),
        "steps": result["input"]["steps"], "nodes": [grouped[key] for key in sorted(grouped)],
        "analysis_id": result["analysisId"], "engine_version": result["engineVersion"],
        "european_price": result["valuation"]["europeanPricePerUnit"],
        "early_exercise_premium": result["valuation"]["earlyExercisePremiumPerUnit"],
    }


def bond_analytics(payload: dict) -> dict:
    """Strict AG-UI adapter over the canonical F-CAL-8 bond engine.

    The adapter adds only the versioned schema discriminator. Dates, decimals,
    quote-mode nullability and position units are otherwise preserved exactly;
    unknown fields and coercible strings fail in the canonical validator.
    """
    if type(payload) is not dict:
        raise ValueError("bond payload must be a JSON object.")
    result = analyze_bond({"schemaVersion": BOND_INPUT_SCHEMA, **payload})
    return {
        "analysis_id": result["analysisId"], "engine_version": result["engineVersion"],
        "clean_price_per_100": result["quote"]["cleanPricePer100"],
        "dirty_price_per_100": result["quote"]["dirtyPricePer100"],
        "accrued_interest_per_100": result["quote"]["accruedInterestPer100"],
        "yield_to_maturity": result["quote"]["yieldToMaturity"],
        "modified_duration": result["analytics"]["modifiedDuration"],
        "convexity": result["analytics"]["convexity"],
        "position_dv01": result["position"]["dv01"],
        "selected_exact_pnl": result["selectedScenario"]["exactPnl"],
        "cashflow_count": len(result["cashflows"]),
    }


def vol_surface_analysis(payload: dict) -> dict:
    """Strict AG-UI adapter over the canonical F-CAL-9 surface engine."""
    if type(payload) is not dict:
        raise ValueError("vol-surface payload must be a JSON object.")
    result = analyze_vol_surface({"schemaVersion": VOL_SURFACE_INPUT_SCHEMA, **payload})
    return {
        "analysis_id": result["analysisId"], "engine_version": result["engineVersion"],
        "status": result["quality"]["status"], "quote_count": result["quality"]["quoteCount"],
        "maturity_count": result["quality"]["maturityCount"], "error_count": result["quality"]["errorCount"],
        "warning_count": result["quality"]["warningCount"],
        "selected_implied_volatility": result["selectedPoint"]["impliedVolatility"],
        "selected_total_variance": result["selectedPoint"]["totalVariance"],
        "diagnostic_codes": [row["code"] for row in result["diagnostics"]],
    }


# Static concept graph for concept_map_block / related concepts.
CONCEPT_GRAPH = {
    "black-scholes": {"central": "Black-Scholes", "prerequisites": ["Mouvement brownien", "Calcul stochastique", "Risk-neutral pricing"], "related": ["Greeks", "Volatilité implicite", "Parité call-put"], "next": "Greeks"},
    "greeks": {"central": "Greeks", "prerequisites": ["Black-Scholes"], "related": ["Delta hedging", "Gamma", "Vega", "Theta"], "next": "Volatilité implicite"},
    "implied-vol": {"central": "Volatilité implicite", "prerequisites": ["Black-Scholes", "Greeks"], "related": ["Smile", "Surface de vol", "Calibration"], "next": "Surfaces de volatilité"},
    "monte-carlo": {"central": "Monte Carlo", "prerequisites": ["Risk-neutral pricing", "Mouvement brownien"], "related": ["Réduction de variance", "Options exotiques", "Convergence"], "next": "Options path-dependent"},
    "exotics": {"central": "Options exotiques", "prerequisites": ["Black-Scholes", "Monte Carlo"], "related": ["Barrière", "Asian", "Lookback", "Digital"], "next": "Produits structurés"},
    "hedging": {"central": "Couverture (hedging)", "prerequisites": ["Greeks"], "related": ["Delta hedging", "Gamma hedging", "P&L de réplication"], "next": "Calibration"},
}


# ---------------------------------------------------------------------------
# Page context extraction (sanitized — never trust/forward secrets)
# ---------------------------------------------------------------------------
SECRET_KEYS = {
    "apikey", "token", "password", "secret", "authorization", "cookie",
    "set-cookie", "privatekey", "refreshtoken", "accesstoken",
}


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            k: ("***" if k.lower().replace("_", "") in SECRET_KEYS else sanitize(v))
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [sanitize(v) for v in value]
    return value


def extract_page_context(payload: dict) -> dict:
    state = payload.get("state") or {}
    fwd = payload.get("forwardedProps") or {}
    merged = {}
    if isinstance(state, dict):
        merged.update(state)
    if isinstance(fwd, dict):
        merged.update(fwd)
    route = merged.get("route") or merged.get("pathname") or "/"
    tool_id = merged.get("toolId") or merged.get("tool")
    if not tool_id and isinstance(route, str) and route.startswith("/tools/"):
        tool_id = route.split("/")[2] if len(route.split("/")) > 2 else None
    parts = [p for p in str(route).split("/") if p]
    page_type = merged.get("pageType") or {
        "": "home", "tools": "tool", "courses": "course", "blog": "blog",
        "exercises": "exercise", "pricing": "pricing", "dashboard": "dashboard",
        "admin": "admin", "community": "community", "lab": "tool", "survival": "exercise",
    }.get(parts[0] if parts else "", "unknown")
    tool_params = sanitize(merged.get("toolParams") or {})
    user = sanitize(merged.get("user") or {})
    current_tool = None
    if tool_id:
        current_tool = {"name": tool_id, "parameters": tool_params, "outputs": sanitize(merged.get("toolOutputs") or {})}
    return {
        "route": route,
        "pathname": route,
        "pageTitle": merged.get("pageTitle"),
        "pageType": page_type,
        "toolId": tool_id,
        "toolParams": tool_params,
        "currentTool": current_tool,
        "courseId": merged.get("courseId"),
        "concept": merged.get("concept"),
        "currentConcepts": merged.get("currentConcepts") or ([merged.get("concept")] if merged.get("concept") else []),
        "visibleFormulas": sanitize(merged.get("visibleFormulas") or []),
        "level": merged.get("level") or "intermediate",
        "user": user,
        "plan": user.get("plan") or merged.get("plan") or "free",
        "lang": merged.get("lang") or "fr",
    }


# ---------------------------------------------------------------------------
# Tool executors — return (result_for_llm: dict, custom_events: list[dict]).
# custom_events are AG-UI Custom events the frontend acts on (render/control).
# ---------------------------------------------------------------------------
def _render_event(block_type: str, props: dict) -> dict | None:
    if block_type not in ALLOWED_UI_BLOCKS:
        return None
    return {
        "type": "Custom",
        "name": "app.render_component",
        "value": {"component": block_type, "props": props},
        "timestamp": _now(),
    }


def tool_rag_search(services: Services, args: dict) -> tuple[dict, list[dict]]:
    query = str(args.get("query") or "").strip()
    top_k = int(args.get("top_k") or 6)
    top_k = max(3, min(top_k, 10))
    if not query:
        return {"error": "query is required"}, []
    resp = services.retriever.search(SearchRequest(query=query, top_k=top_k))
    sources = [
        {
            "title": r.title or r.source or r.document_id,
            "snippet": (r.snippet or "")[:600],
            "score": round(r.score, 3),
            "chunk_index": r.chunk_index,
        }
        for r in resp.results
    ]
    events = []
    if sources:
        ev = _render_event("source_card", {"query": query, "sources": sources})
        if ev:
            events.append(ev)
    return {"query": query, "count": len(sources), "sources": sources}, events


def tool_black_scholes(services: Services, args: dict) -> tuple[dict, list[dict]]:
    try:
        p = _base_params(args)
        result = black_scholes(p["S"], p["K"], p["r"], p["q"], p["sigma"], p["T"])
    except ValueError as exc:
        return {"error": str(exc)}, []
    metrics = [
        {"label": "Call", "value": result.get("call")},
        {"label": "Put", "value": result.get("put")},
        {"label": "C - P", "value": result.get("parity_lhs")},
        {"label": "S·e^{-qT} - K·e^{-rT}", "value": result.get("parity_rhs")},
    ]
    ev = _render_event("metric_grid", {"title": "Black-Scholes (vérifié)", "metrics": metrics})
    return result, ([ev] if ev else [])


def tool_set_tool_params(services: Services, args: dict) -> tuple[dict, list[dict]]:
    tool = str(args.get("tool") or "").strip()
    params = args.get("params") or {}
    if tool not in KNOWN_TOOLS:
        return {"error": f"unknown tool '{tool}'", "known": sorted(KNOWN_TOOLS)}, []
    if not isinstance(params, dict):
        return {"error": "params must be an object"}, []
    event = {
        "type": "Custom",
        "name": "app.tool.set_params",
        "value": {"tool": tool, "params": params},
        "timestamp": _now(),
    }
    return {"ok": True, "tool": tool, "params": params}, [event]


def tool_navigate(services: Services, args: dict) -> tuple[dict, list[dict]]:
    path = str(args.get("path") or "").strip()
    if not path.startswith("/"):
        return {"error": "path must start with /"}, []
    event = {"type": "Custom", "name": "app.navigate", "value": {"path": path}, "timestamp": _now()}
    return {"ok": True, "path": path}, [event]


def tool_generate_exercise(services: Services, args: dict) -> tuple[dict, list[dict]]:
    req = ExerciseRequest(
        topic=args.get("topic"),
        product=args.get("product"),
        concept=args.get("concept"),
        free_prompt=args.get("free_prompt"),
        difficulty=args.get("difficulty") or "intermediate",
        exercise_format=args.get("exercise_format") or "mixed",
        number_of_questions=int(args.get("number_of_questions") or 4),
        language=args.get("language") or "fr",
    )
    try:
        gen = services.generator.generate_exercise(req)
    except Exception as exc:  # pragma: no cover - defensive
        return {"error": f"generation failed: {exc}"}, []
    pack = (gen.metadata or {}).get("calculation_pack")
    sources = [
        {"title": s.title or s.source or s.document_id, "score": round(s.score, 3)}
        for s in gen.sources[:6]
    ]
    ev = _render_event(
        "exercise_block",
        {
            "title": gen.title,
            "markdown": gen.content,
            "sources": sources,
            "calculation_pack": pack,
        },
    )
    return (
        {"title": gen.title, "preview": gen.content[:400], "has_calculation": bool(pack)},
        ([ev] if ev else []),
    )


def tool_render_block(services: Services, args: dict) -> tuple[dict, list[dict]]:
    block_type = str(args.get("type") or "").strip()
    props = args.get("props") or {}
    ev = _render_event(block_type, props if isinstance(props, dict) else {})
    if ev is None:
        return {"error": f"block type '{block_type}' not allowed", "allowed": sorted(ALLOWED_UI_BLOCKS)}, []
    return {"ok": True, "type": block_type}, [ev]


def _base_params(args: dict, extra_keys: tuple[str, ...] = ()) -> dict:
    if type(args) is not dict:
        raise ValueError("arguments must be a plain object.")
    allowed = {"S", "K", "r", "q", "sigma", "T", *extra_keys}
    unknown = sorted(set(args) - allowed)
    if unknown:
        raise ValueError(f"unknown parameters: {'|'.join(unknown)}.")
    defaults = {"S": 100, "K": 100, "r": 2, "q": 0, "sigma": 20, "T": 180}
    values = {key: args.get(key, default) for key, default in defaults.items()}
    # Canonical normalization is the single numerical/domain validator.
    analyze_black_scholes(_canonical_bs_input(values["S"], values["K"], values["r"], values["q"], values["sigma"], values["T"]))
    return values


def tool_compute_greeks(services: Services, args: dict) -> tuple[dict, list[dict]]:
    try:
        p = _base_params(args)
        g = bs_full(p["S"], p["K"], p["r"], p["q"], p["sigma"], p["T"])
    except ValueError as exc:
        return {"error": str(exc)}, []
    ev = _render_event("black_scholes_explorer_block", {"params": p, "result": g})
    return g, ([ev] if ev else [])


def tool_put_call_parity(services: Services, args: dict) -> tuple[dict, list[dict]]:
    try:
        p = _base_params(args)
        bs = black_scholes(p["S"], p["K"], p["r"], p["q"], p["sigma"], p["T"])
    except ValueError as exc:
        return {"error": str(exc)}, []
    ev = _render_event("put_call_parity_block", {"params": p, "result": bs})
    return bs, ([ev] if ev else [])


def tool_greeks_sensitivity(services: Services, args: dict) -> tuple[dict, list[dict]]:
    try:
        greek = args.get("greek", "vega")
        param = args.get("param", "time")
        if type(greek) is not str or type(param) is not str:
            raise ValueError("greek and param must be strings.")
        data = greeks_sensitivity(greek, param, _base_params(args, ("greek", "param")))
    except ValueError as exc:
        return {"error": str(exc)}, []
    ev = _render_event("greeks_sensitivity_block", data)
    return {"greek": greek, "param": param, "points": len(data["series"])}, ([ev] if ev else [])


def tool_simulate_monte_carlo(services: Services, args: dict) -> tuple[dict, list[dict]]:
    data = mc_simulation(
        args.get("S", 100), args.get("mu", 5), args.get("sigma", 20),
        args.get("T", 252), args.get("N", 400), args.get("steps", 50), args.get("seed", 7),
    )
    ev = _render_event("monte_carlo_simulation_block", data)
    summary = {k: data[k] for k in ("terminal_mean", "p5", "p95", "n", "steps", "analysis_id", "engine_version", "measure", "day_count")}
    return summary, ([ev] if ev else [])


def tool_generate_payoff_scenario(services: Services, args: dict) -> tuple[dict, list[dict]]:
    legs = args.get("legs") or []
    if not isinstance(legs, list) or not legs:
        return {"error": "legs[] required"}, []
    data = payoff_series(legs)
    ev = _render_event("payoff_chart_block", {"name": args.get("name") or "Payoff", "legs": legs, **data})
    return {"breakevens": data["breakevens"], "max_gain": data["max_gain"], "max_loss": data["max_loss"]}, ([ev] if ev else [])


def tool_build_structured_product(services: Services, args: dict) -> tuple[dict, list[dict]]:
    kind = str(args.get("kind") or "autocall")
    data = structured_payoff(kind, args.get("params") or {})
    ev = _render_event("structured_product_payoff_block", data)
    return {"kind": kind, "scenarios": data["scenarios"]}, ([ev] if ev else [])


def tool_binomial_tree(services: Services, args: dict) -> tuple[dict, list[dict]]:
    data = binomial_tree(
        args.get("S", 100), args.get("K", 100), args.get("r", 2),
        args.get("sigma", 20), args.get("T", 180), args.get("steps", 4),
        args.get("kind", "call"), args.get("american", False), args.get("q", 0),
    )
    ev = _render_event("binomial_tree_block", data)
    return {"price": data["price"], "p": data["p"], "steps": data["steps"], "analysis_id": data["analysis_id"], "engine_version": data["engine_version"]}, ([ev] if ev else [])


def tool_bond_analytics(services: Services, args: dict) -> tuple[dict, list[dict]]:
    return bond_analytics(args), []


def tool_vol_surface_analysis(services: Services, args: dict) -> tuple[dict, list[dict]]:
    return vol_surface_analysis(args), []


def tool_grade_user_answer(services: Services, args: dict) -> tuple[dict, list[dict]]:
    block = {
        "verdict": args.get("verdict") or "partial",
        "correct": args.get("correct") or [],
        "wrong": args.get("wrong") or [],
        "improve": args.get("improve") or [],
        "solution": args.get("solution") or "",
        "score": args.get("score"),
    }
    ev = _render_event("answer_feedback_block", block)
    return {"ok": True, "verdict": block["verdict"]}, ([ev] if ev else [])


def tool_related_concepts(services: Services, args: dict) -> tuple[dict, list[dict]]:
    key = str(args.get("concept") or "").lower().replace(" ", "-")
    graph = CONCEPT_GRAPH.get(key) or CONCEPT_GRAPH.get(args.get("courseId", ""), None)
    if not graph:
        graph = {"central": args.get("concept") or "Concept", "prerequisites": [], "related": [], "next": None}
    ev = _render_event("concept_map_block", graph)
    return graph, ([ev] if ev else [])


TOOL_EXECUTORS: dict[str, Callable[[Services, dict], tuple[dict, list[dict]]]] = {
    "rag_search": tool_rag_search,
    "compute_black_scholes": tool_black_scholes,
    "compute_greeks": tool_compute_greeks,
    "compute_put_call_parity": tool_put_call_parity,
    "greeks_sensitivity": tool_greeks_sensitivity,
    "simulate_monte_carlo": tool_simulate_monte_carlo,
    "generate_payoff_scenario": tool_generate_payoff_scenario,
    "build_structured_product_payoff": tool_build_structured_product,
    "binomial_tree": tool_binomial_tree,
    "bond_analytics": tool_bond_analytics,
    "vol_surface_analysis": tool_vol_surface_analysis,
    "grade_user_answer": tool_grade_user_answer,
    "get_related_concepts": tool_related_concepts,
    "set_tool_params": tool_set_tool_params,
    "navigate": tool_navigate,
    "generate_exercise": tool_generate_exercise,
    "render_block": tool_render_block,
}


def openai_tool_specs() -> list[dict]:
    """OpenAI function-calling schemas for the executors above."""
    return [
        {
            "type": "function",
            "function": {
                "name": "rag_search",
                "description": (
                    "Search the local market-finance knowledge base (RAG) for grounded "
                    "excerpts. Use this before answering a conceptual question so your answer "
                    "is sourced. Renders source cards for the user."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query in the page language."},
                        "top_k": {"type": "integer", "minimum": 3, "maximum": 10},
                    },
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "compute_black_scholes",
                "description": (
                    "Compute verified Black-Scholes call/put prices, delta, vega and the "
                    "call-put parity check. Units: r,q,sigma in percent, T in days (same as the "
                    "BS pricer tool)."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "S": {"type": "number"}, "K": {"type": "number"},
                        "r": {"type": "number"}, "q": {"type": "number"},
                        "sigma": {"type": "number"}, "T": {"type": "number"},
                    },
                    "required": ["S", "K", "sigma", "T"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "set_tool_params",
                "description": (
                    "Take control of an on-page interactive tool and set its parameters to "
                    "demonstrate a concept. tool is one of: bs-pricer, payoff, mc, iv-calc, "
                    "calib, binomial, bond, curve, volsurface. For bs-pricer params keys: S,K,r,q,sigma,T,view "
                    "(view in spot|vol|time). For payoff params: legs=[{type:call|put,side:"
                    "long|short,K,qty,prem}] to build a structured-product payoff."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tool": {"type": "string"},
                        "params": {"type": "object"},
                    },
                    "required": ["tool", "params"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "navigate",
                "description": "Navigate the SPA to an internal path (e.g. /tools/bs-pricer) before driving a tool.",
                "parameters": {
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "generate_exercise",
                "description": (
                    "Generate a grounded, verified practice exercise (with a deterministic "
                    "calculation pack) on a topic. Renders an exercise block."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "product": {"type": "string"},
                        "concept": {"type": "string"},
                        "difficulty": {"type": "string", "enum": ["beginner", "intermediate", "advanced", "expert"]},
                        "language": {"type": "string", "enum": ["fr", "en"]},
                    },
                    "required": ["topic"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "compute_greeks",
                "description": "Compute full Black-Scholes Greeks (delta, gamma, vega, theta, rho) and render a Black-Scholes explorer block. Units: r,q,sigma percent; T days.",
                "parameters": {"type": "object", "properties": {"S": {"type": "number"}, "K": {"type": "number"}, "r": {"type": "number"}, "q": {"type": "number"}, "sigma": {"type": "number"}, "T": {"type": "number"}}, "required": ["S", "K", "sigma", "T"], "additionalProperties": False},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "compute_put_call_parity",
                "description": "Verify the call-put parity C - P = S e^{-qT} - K e^{-rT} and render a put_call_parity_block. Use this when demonstrating parity.",
                "parameters": {"type": "object", "properties": {"S": {"type": "number"}, "K": {"type": "number"}, "r": {"type": "number"}, "q": {"type": "number"}, "sigma": {"type": "number"}, "T": {"type": "number"}}, "required": ["S", "K", "sigma", "T"], "additionalProperties": False},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "greeks_sensitivity",
                "description": "Render how a Greek evolves as one parameter varies (great for visual intuition, e.g. vega vs maturity). greek in delta|gamma|vega|theta|rho; param in spot|vol|time|strike.",
                "parameters": {"type": "object", "properties": {"greek": {"type": "string", "enum": ["delta", "gamma", "vega", "theta", "rho", "call", "put"]}, "param": {"type": "string", "enum": ["spot", "vol", "time", "strike"]}, "S": {"type": "number"}, "K": {"type": "number"}, "r": {"type": "number"}, "q": {"type": "number"}, "sigma": {"type": "number"}, "T": {"type": "number"}}, "required": ["greek", "param"], "additionalProperties": False},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "simulate_monte_carlo",
                "description": "Run a pedagogical GBM Monte Carlo simulation and render paths + terminal distribution + confidence interval.",
                "parameters": {"type": "object", "properties": {"S": {"type": "number"}, "mu": {"type": "number"}, "sigma": {"type": "number"}, "T": {"type": "number"}, "N": {"type": "integer"}}, "required": ["S", "sigma", "T"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "generate_payoff_scenario",
                "description": "Render the expiry payoff chart of an option strategy. legs=[{type:call|put,side:long|short,K,qty,prem}].",
                "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "legs": {"type": "array", "items": {"type": "object"}}}, "required": ["legs"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "build_structured_product_payoff",
                "description": "Render a simplified structured-product terminal payoff + repayment scenarios. kind in autocall|capital_protected|reverse_convertible|barrier_note|participation. params may include barrier(%), coupon(%), participation(%), protection(%).",
                "parameters": {"type": "object", "properties": {"kind": {"type": "string"}, "params": {"type": "object"}}, "required": ["kind"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "binomial_tree",
                "description": "Price a European or American option with the canonical CRR engine. Rates/vol are percentages, T is days, and invalid no-arbitrage probabilities fail closed.",
                "parameters": {"type": "object", "properties": {"S": {"type": "number"}, "K": {"type": "number"}, "r": {"type": "number"}, "q": {"type": "number"}, "sigma": {"type": "number"}, "T": {"type": "number"}, "steps": {"type": "integer", "minimum": 2, "maximum": 2000}, "kind": {"type": "string", "enum": ["call", "put"]}, "american": {"type": "boolean"}}, "required": ["S", "K", "sigma", "T"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "bond_analytics",
                "description": "Price a regular fixed-rate bullet bond with the canonical F-CAL-8 engine. Inputs use ISO dates and decimal coupon/yield; quoteMode is yield or clean_price. Returns clean/dirty/accrued, solved YTM, duration, convexity, signed DV01 and exact shock P&L.",
                "parameters": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "settlementDate": {"type": "string", "format": "date"},
                        "maturityDate": {"type": "string", "format": "date"},
                        "dayCount": {"type": "string", "enum": ["ACT/ACT ICMA", "30E/360"]},
                        "couponRate": {"type": "number", "minimum": 0, "maximum": 1},
                        "couponFrequency": {"type": "integer", "enum": [1, 2, 4, 12]},
                        "quoteMode": {"type": "string", "enum": ["yield", "clean_price"]},
                        "yieldToMaturity": {"type": ["number", "null"]},
                        "cleanPrice": {"type": ["number", "null"]},
                        "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
                        "notional": {"type": "number", "exclusiveMinimum": 0},
                        "position": {"type": "string", "enum": ["long", "short"]},
                        "shockBp": {"type": "number", "minimum": -5000, "maximum": 5000},
                    },
                    "required": ["settlementDate", "maturityDate", "dayCount", "couponRate", "couponFrequency", "quoteMode", "yieldToMaturity", "cleanPrice", "currency", "notional", "position", "shockBp"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "vol_surface_analysis",
                "description": "Analyze a rectangular implied-volatility surface with the canonical F-CAL-9 engine. Volatilities are annualized decimals; k is ln(K/F). Returns total-variance interpolation and discrete bound, vertical, butterfly and calendar diagnostics without repair.",
                "parameters": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "surfaceName": {"type": "string", "minLength": 1, "maxLength": 80},
                        "asOfDate": {"type": "string", "format": "date"},
                        "sourceKind": {"type": "string", "enum": ["deterministic_fixture", "user_csv"]},
                        "interpolationMode": {"type": "string", "enum": ["total_variance_bilinear"]},
                        "selectedMaturity": {"type": "number"},
                        "selectedLogMoneyness": {"type": "number"},
                        "quotes": {"type": "array", "minItems": 10, "maxItems": 500, "items": {"type": "object", "additionalProperties": False, "properties": {"maturity": {"type": "number"}, "forward": {"type": "number"}, "discountFactor": {"type": "number"}, "logMoneyness": {"type": "number"}, "impliedVolatility": {"type": "number"}, "bidVolatility": {"type": ["number", "null"]}, "askVolatility": {"type": ["number", "null"]}}, "required": ["maturity", "forward", "discountFactor", "logMoneyness", "impliedVolatility", "bidVolatility", "askVolatility"]}},
                    },
                    "required": ["surfaceName", "asOfDate", "sourceKind", "interpolationMode", "selectedMaturity", "selectedLogMoneyness", "quotes"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "grade_user_answer",
                "description": "Render a personalized correction of the user's answer to an exercise. Provide your assessment fields.",
                "parameters": {"type": "object", "properties": {"verdict": {"type": "string", "enum": ["correct", "partial", "incorrect"]}, "correct": {"type": "array", "items": {"type": "string"}}, "wrong": {"type": "array", "items": {"type": "string"}}, "improve": {"type": "array", "items": {"type": "string"}}, "solution": {"type": "string"}, "score": {"type": "number"}}, "required": ["verdict"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_related_concepts",
                "description": "Render a concept map (prerequisites, related concepts, next concept) for a financial concept.",
                "parameters": {"type": "object", "properties": {"concept": {"type": "string"}}, "required": ["concept"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "render_block",
                "description": (
                    "Render a typed pedagogical UIBlock you author yourself. Use for: "
                    "latex_formula_block {latex, caption}; derivation_steps_block {title, steps:[{label, latex}]}; "
                    "quiz_block {question, options:[{id,label}], answer, explanation}; summary_card {title, points:[...]}; "
                    "action_card {title, description, actions:[{label}]}; progress_steps {steps:[{label, done}]}; "
                    "concept_map_block {central, prerequisites:[...], related:[...], next}. Never put executable code."
                ),
                "parameters": {"type": "object", "properties": {"type": {"type": "string"}, "props": {"type": "object"}}, "required": ["type", "props"]},
            },
        },
    ]


# ---------------------------------------------------------------------------
# System prompt (page-aware, educational, markdown + LaTeX)
# ---------------------------------------------------------------------------
def build_system_prompt(ctx: dict) -> str:
    tool_line = ""
    if ctx.get("toolId"):
        tool_line = (
            f"\nThe user is currently on the interactive tool '{ctx['toolId']}'. "
            f"Current tool parameters: {json.dumps(ctx.get('toolParams') or {}, ensure_ascii=False)}. "
            "You may take control of it with set_tool_params to demonstrate a concept "
            "(e.g. set the BS pricer to S=K to illustrate call-put parity), then explain what the user should observe."
        )
    return (
        "Tu es le **Quant Tutor Agent** de The Pricing Library : un professeur particulier de "
        "finance quantitative (pricing d'options, produits dérivés, risk) intégré au site.\n"
        "Objectif: rendre l'apprentissage vivant — comprendre la page, expliquer la notion, "
        "montrer visuellement, faire pratiquer, corriger.\n"
        f"Contexte page: route={ctx.get('route')} | type={ctx.get('pageType')} | titre={ctx.get('pageTitle')} | "
        f"concepts={ctx.get('currentConcepts')} | niveau={ctx.get('level')} | plan={ctx.get('plan')} | langue={ctx.get('lang')}."
        f"{tool_line}\n\n"
        "Outils disponibles (utilise-les, ne les simule pas):\n"
        "- rag_search → fonde tes explications conceptuelles sur le corpus interne et cite les sources.\n"
        "- compute_black_scholes / compute_greeks / compute_put_call_parity / binomial_tree / bond_analytics / vol_surface_analysis → nombres VÉRIFIÉS.\n"
        "- greeks_sensitivity → montre l'évolution d'un Greek selon un paramètre (intuition visuelle).\n"
        "- simulate_monte_carlo → trajectoires + distribution terminale.\n"
        "- generate_payoff_scenario (stratégies d'options) / build_structured_product_payoff (autocall, capital protégé, reverse convertible...).\n"
        "- generate_exercise → exercice avec corrigé chiffré ; grade_user_answer → corrige la réponse de l'élève.\n"
        "- get_related_concepts → carte conceptuelle (prérequis / liés / suivant).\n"
        "- set_tool_params (+ navigate) → pilote l'outil de la page pour démontrer une notion.\n"
        "- render_block → compose toi-même un bloc pédagogique typé (latex_formula_block, derivation_steps_block, "
        "quiz_block, summary_card, action_card, progress_steps, concept_map_block).\n\n"
        "Règles:\n"
        "- Réponds dans la langue de la page (français si lang=fr). Adapte la profondeur au niveau "
        "(vulgarise si beginner, va plus loin mathématiquement si advanced).\n"
        "- N'invente JAMAIS de chiffres ni de sources RAG. Si le corpus ne contient rien, dis-le et réponds "
        "avec tes connaissances générales en précisant que ce n'est pas sourcé par le corpus interne.\n"
        "- Formate en Markdown. Mathématiques en LaTeX ($...$ en ligne, $$...$$ en bloc).\n"
        "- Sur une page tool, privilégie set_tool_params pour montrer, puis explique l'observation.\n"
        "- Aucune action sensible (modification/publication de contenu, admin) sans confirmation explicite "
        "(émets alors un confirmation_card via render_block et attends la validation).\n"
        "- Sois pédagogue, progressif, orienté intuition + rigueur."
    )


# ---------------------------------------------------------------------------
# OpenAI client
# ---------------------------------------------------------------------------
def _openai_client(services: Services):
    from openai import OpenAI

    s = services.settings
    kwargs = {"api_key": s.openai_api_key, "timeout": s.openai_timeout_seconds, "max_retries": s.openai_max_retries}
    if s.openai_base_url:
        kwargs["base_url"] = s.openai_base_url
    return OpenAI(**kwargs)


def _map_messages(payload: dict) -> list[dict]:
    out = []
    for m in payload.get("messages") or []:
        role = m.get("role")
        content = m.get("content")
        if role in ("user", "assistant", "system") and isinstance(content, str) and content.strip():
            out.append({"role": role, "content": content})
    # Guardrail: only forward the most recent turns to bound prompt size/cost.
    if len(out) > MAX_HISTORY_MESSAGES:
        out = out[-MAX_HISTORY_MESSAGES:]
    return out


# ---------------------------------------------------------------------------
# OpenAI streaming agent loop
# ---------------------------------------------------------------------------
def _run_openai_agent(services: Services, payload: dict, ctx: dict) -> Iterator[dict]:
    client = _openai_client(services)
    model = services.settings.openai_model or "gpt-4o-mini"
    tools = openai_tool_specs()

    messages = [{"role": "system", "content": build_system_prompt(ctx)}]
    messages.extend(_map_messages(payload))

    total_tokens = 0  # cumulative across steps — guardrail budget

    for _step in range(MAX_AGENT_STEPS):
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            temperature=0.3,
            stream=True,
            max_tokens=MAX_OUTPUT_TOKENS,
            stream_options={"include_usage": True},
        )

        text_id = _new_id("msg")
        text_started = False
        text_buf: list[str] = []
        tool_calls: dict[int, dict] = {}
        finish_reason = None

        for chunk in stream:
            usage = getattr(chunk, "usage", None)
            if usage is not None:
                total_tokens += getattr(usage, "total_tokens", 0) or 0
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            delta = choice.delta
            if choice.finish_reason:
                finish_reason = choice.finish_reason
            if getattr(delta, "content", None):
                if not text_started:
                    text_started = True
                    yield {"type": "TextMessageStart", "messageId": text_id, "role": "assistant"}
                text_buf.append(delta.content)
                yield {"type": "TextMessageContent", "messageId": text_id, "delta": delta.content}
            for tc in (getattr(delta, "tool_calls", None) or []):
                idx = tc.index
                slot = tool_calls.setdefault(idx, {"id": None, "name": "", "args": ""})
                if tc.id:
                    slot["id"] = tc.id
                if tc.function and tc.function.name:
                    slot["name"] = tc.function.name
                if tc.function and tc.function.arguments:
                    slot["args"] += tc.function.arguments

        if text_started:
            yield {"type": "TextMessageEnd", "messageId": text_id}

        if finish_reason != "tool_calls" or not tool_calls:
            return

        # Record the assistant turn (text + tool call requests) for the loop.
        assistant_msg: dict = {"role": "assistant", "content": "".join(text_buf) or None}
        assistant_msg["tool_calls"] = [
            {
                "id": slot["id"] or _new_id("call"),
                "type": "function",
                "function": {"name": slot["name"], "arguments": slot["args"] or "{}"},
            }
            for slot in tool_calls.values()
        ]
        messages.append(assistant_msg)

        for call in assistant_msg["tool_calls"]:
            name = call["function"]["name"]
            call_id = call["id"]
            raw_args = call["function"]["arguments"]
            try:
                args = json.loads(raw_args) if raw_args else {}
            except json.JSONDecodeError:
                args = {}
            yield {"type": "ToolCallStart", "toolCallId": call_id, "toolCallName": name}
            yield {"type": "ToolCallArgs", "toolCallId": call_id, "delta": raw_args or "{}"}
            yield {"type": "ToolCallEnd", "toolCallId": call_id}

            executor = TOOL_EXECUTORS.get(name)
            if executor is None:
                result, events = {"error": f"unknown tool '{name}'"}, []
            else:
                try:
                    result, events = executor(services, args)
                except Exception as exc:  # pragma: no cover - defensive
                    result, events = {"error": str(exc)}, []

            yield {
                "type": "ToolCallResult",
                "messageId": _new_id("toolmsg"),
                "toolCallId": call_id,
                "content": json.dumps(result, ensure_ascii=False),
                "role": "tool",
            }
            for ev in events:
                yield ev
            messages.append(
                {"role": "tool", "tool_call_id": call_id, "content": json.dumps(result, ensure_ascii=False)}
            )

        # Guardrail: stop before spending another LLM call if the per-run
        # token budget is exhausted.
        if total_tokens >= MAX_TOTAL_TOKENS:
            note_id = _new_id("msg")
            yield {"type": "TextMessageStart", "messageId": note_id, "role": "assistant"}
            yield {
                "type": "TextMessageContent",
                "messageId": note_id,
                "delta": "\n\n_(Limite de coût atteinte pour cette réponse — relance si tu veux que je continue.)_",
            }
            yield {"type": "TextMessageEnd", "messageId": note_id}
            return
    # If we exhausted MAX_AGENT_STEPS, stop quietly.


# ---------------------------------------------------------------------------
# Offline (no-LLM-cost) intent-based agent — still uses real retrieval/calc.
# ---------------------------------------------------------------------------
def _emit_text(text: str) -> Iterator[dict]:
    mid = _new_id("msg")
    yield {"type": "TextMessageStart", "messageId": mid, "role": "assistant"}
    # Stream in word groups so the frontend animation works offline too.
    words = text.split(" ")
    chunk = []
    for w in words:
        chunk.append(w)
        if len(chunk) >= 6:
            yield {"type": "TextMessageContent", "messageId": mid, "delta": " ".join(chunk) + " "}
            chunk = []
    if chunk:
        yield {"type": "TextMessageContent", "messageId": mid, "delta": " ".join(chunk)}
    yield {"type": "TextMessageEnd", "messageId": mid}


def _last_user_text(payload: dict) -> str:
    for m in reversed(payload.get("messages") or []):
        if m.get("role") == "user" and isinstance(m.get("content"), str):
            return m["content"]
    return ""


def _tool_call_sequence(services: Services, name: str, args: dict) -> Iterator[dict]:
    call_id = _new_id("call")
    yield {"type": "ToolCallStart", "toolCallId": call_id, "toolCallName": name}
    yield {"type": "ToolCallArgs", "toolCallId": call_id, "delta": json.dumps(args, ensure_ascii=False)}
    yield {"type": "ToolCallEnd", "toolCallId": call_id}
    executor = TOOL_EXECUTORS.get(name)
    result, events = executor(services, args) if executor else ({"error": "unknown"}, [])
    yield {
        "type": "ToolCallResult",
        "messageId": _new_id("toolmsg"),
        "toolCallId": call_id,
        "content": json.dumps(result, ensure_ascii=False),
        "role": "tool",
    }
    for ev in events:
        yield ev


def _run_offline_agent(services: Services, payload: dict, ctx: dict) -> Iterator[dict]:
    text = _last_user_text(payload).lower()
    tool_id = ctx.get("toolId")

    # Intent: call-put parity demo on the BS pricer.
    if ("parit" in text or "call-put" in text or "call put" in text) and (
        tool_id == "bs-pricer" or "black" in text or "scholes" in text
    ):
        if tool_id != "bs-pricer":
            yield from _tool_call_sequence(services, "navigate", {"path": "/tools/bs-pricer"})
        params = {"S": 100, "K": 100, "r": 2, "q": 0, "sigma": 20, "T": 180, "view": "spot"}
        yield from _tool_call_sequence(services, "set_tool_params", {"tool": "bs-pricer", "params": params})
        yield from _tool_call_sequence(services, "compute_black_scholes", {key: params[key] for key in ("S", "K", "r", "q", "sigma", "T")})
        bs = black_scholes(100, 100, 2, 0, 20, 180)
        yield from _emit_text(
            "J'ai réglé le pricer en **at-the-money** ($S=K=100$). Observe la **parité call-put** : "
            "$$C - P = S e^{-qT} - K e^{-rT}.$$ "
            f"Ici $C-P = {bs['parity_lhs']}$ et $S e^{{-qT}} - K e^{{-rT}} = {bs['parity_rhs']}$ — "
            "les deux coïncident, ce qui confirme la relation sans arbitrage. Fais varier le taux $r$ : "
            "l'écart call−put suit la valeur actualisée du strike."
        )
        yield from _tool_call_sequence(services, "rag_search", {"query": "call put parity black scholes", "top_k": 5})
        return

    # Intent: Greek sensitivity (e.g. "vega quand la maturité augmente").
    if any(g in text for g in ("vega", "gamma", "theta", "delta", "rho")) and any(
        k in text for k in ("maturit", "échéance", "echeance", "augmente", "sensib", "varie", "évolue", "evolue", "quand")
    ):
        greek = next((g for g in ("vega", "gamma", "theta", "delta", "rho") if g in text), "vega")
        param = "time" if any(k in text for k in ("maturit", "échéance", "echeance", "temps")) else (
            "vol" if "vol" in text else ("strike" if "strike" in text else "spot"))
        yield from _tool_call_sequence(services, "greeks_sensitivity", {"greek": greek, "param": param})
        param_fr = {"time": "la maturité", "vol": "la volatilité", "strike": "le strike"}.get(param, "le spot")
        greek_note = {
            "delta": "le delta d'un call varie de 0 à 1 avec le spot : c'est ton ratio de couverture en actions.",
            "gamma": "le gamma culmine à la monnaie et explose près de l'échéance : c'est l'instabilité de ton delta.",
            "vega": "le vega culmine à la monnaie et croît avec la maturité : c'est ton exposition à la vol implicite.",
            "theta": "le theta est négatif pour une option longue : c'est le coût du temps qui passe, payé chaque jour.",
            "rho": "le rho mesure la sensibilité au taux : faible en général, sauf sur longue maturité.",
        }.get(greek, "")
        yield from _emit_text(
            f"Voici l'évolution du **{greek}** en fonction de {param_fr}. "
            f"Lis la courbe ci-dessus : {greek_note} Le pic et le signe te disent où la sensibilité est la plus "
            "forte et dans quel sens couvrir. Demande-moi un autre Greek ou un autre paramètre."
        )
        return

    # Intent: Monte Carlo simulation.
    if "monte" in text or "simulation" in text or "trajectoir" in text:
        yield from _tool_call_sequence(services, "simulate_monte_carlo", {"S": 100, "mu": 5, "sigma": 20, "T": 252, "N": 400})
        yield from _emit_text(
            "Simulation GBM ci-dessus : quelques trajectoires, la **distribution terminale** et un "
            "intervalle de confiance à 90% (p5–p95). Le prix d'une option s'estime comme la moyenne "
            "actualisée du payoff sur ces trajectoires ; la précision croît en $1/\\sqrt{N}$."
        )
        return

    # Intent: structured product payoff.
    if "autocall" in text or "structur" in text or "capital prot" in text or "reverse convert" in text:
        kind = "autocall" if "autocall" in text else (
            "capital_protected" if "capital" in text else (
                "reverse_convertible" if "reverse" in text else "autocall"))
        params = {"barrier": 60, "coupon": 8}
        yield from _tool_call_sequence(services, "build_structured_product_payoff", {"kind": kind, "params": params})
        yield from _emit_text(
            "Voici le payoff simplifié à maturité (ci-dessus) avec les scénarios de remboursement. "
            "Pour un **autocall** : coupon si le sous-jacent finit au-dessus du niveau initial, capital "
            "protégé tant que la barrière (60%) n'est pas franchie à la baisse, sinon perte en capital. "
            "Dis-moi les paramètres (barrière, coupon) et je régénère."
        )
        return

    # Intent: option strategy payoff. Parse WHICH strategy was asked (not always a
    # bull call spread) so "long straddle" no longer renders a mislabeled spread.
    if "payoff" in text or "spread" in text or "straddle" in text or "strangle" in text or "butterfly" in text:
        if tool_id != "payoff":
            yield from _tool_call_sequence(services, "navigate", {"path": "/tools/payoff"})
        if "straddle" in text:
            name = "Long straddle"
            legs = [
                {"type": "call", "side": "long", "K": 100, "qty": 1, "prem": 4},
                {"type": "put", "side": "long", "K": 100, "qty": 1, "prem": 3.8},
            ]
            desc = ("Un **long straddle** (long call ET long put au même strike $K=100$) : tu paies les deux primes "
                    "et tu gagnes si le sous-jacent bouge fort, dans n'importe quel sens. C'est un pari long volatilité.")
        elif "strangle" in text:
            name = "Long strangle"
            legs = [
                {"type": "put", "side": "long", "K": 90, "qty": 1, "prem": 2.1},
                {"type": "call", "side": "long", "K": 110, "qty": 1, "prem": 2.3},
            ]
            desc = ("Un **long strangle** (long put $K=90$, long call $K=110$) : moins cher que le straddle, mais il "
                    "faut un mouvement plus ample pour être rentable. Long volatilité, zone morte plus large.")
        elif "butterfly" in text or "papillon" in text:
            name = "Long call butterfly"
            legs = [
                {"type": "call", "side": "long", "K": 90, "qty": 1, "prem": 12},
                {"type": "call", "side": "short", "K": 100, "qty": 2, "prem": 5},
                {"type": "call", "side": "long", "K": 110, "qty": 1, "prem": 1.6},
            ]
            desc = ("Un **long butterfly** (long 90, short 2× 100, long 110) : gain maximal si le sous-jacent finit "
                    "pile à 100, perte limitée à la prime nette. C'est un pari court volatilité, sur un point précis.")
        elif "bear" in text:
            name = "Bear put spread"
            legs = [
                {"type": "put", "side": "long", "K": 100, "qty": 1, "prem": 4},
                {"type": "put", "side": "short", "K": 80, "qty": 1, "prem": 1.2},
            ]
            desc = ("Un **bear put spread** (long put $K=100$, short put $K=80$) : tu gagnes à la baisse, gain plafonné, "
                    "coût net réduit par la prime encaissée.")
        else:
            name = "Bull call spread"
            legs = [
                {"type": "call", "side": "long", "K": 100, "qty": 1, "prem": 4},
                {"type": "call", "side": "short", "K": 120, "qty": 1, "prem": 1.2},
            ]
            desc = ("Un **bull call spread** (long call $K=100$, short call $K=120$) : gain plafonné, coût net réduit "
                    "par la prime encaissée. Payoff $\\max(S-100,0)-\\max(S-120,0)$ moins la prime nette.")
        yield from _tool_call_sequence(services, "set_tool_params", {"tool": "payoff", "params": {"legs": legs}})
        yield from _tool_call_sequence(services, "generate_payoff_scenario", {"name": name, "legs": legs})
        yield from _emit_text("Voici un " + desc + " Dis-moi les strikes ou une autre stratégie et je régénère.")
        return

    # Intent: grade the user's answer.
    if "corrige" in text or "ma réponse" in text or "ma reponse" in text or "vérifie ma" in text:
        yield from _tool_call_sequence(services, "grade_user_answer", {
            "verdict": "partial",
            "correct": ["Tu as identifié le bon concept."],
            "wrong": ["Mode hors-ligne : je ne peux pas évaluer finement sans le LLM."],
            "improve": ["Active le mode OpenAI pour une correction détaillée et personnalisée."],
            "solution": "Relance avec la clé OpenAI configurée pour une correction complète.",
        })
        yield from _emit_text("Voici un retour préliminaire (correction détaillée disponible en mode OpenAI).")
        return

    # Intent: generate an exercise.
    if "exercice" in text or "exercise" in text or "entra" in text or "quiz" in text:
        topic = ctx.get("concept") or ctx.get("pageTitle") or "pricing d'options"
        yield from _tool_call_sequence(
            services, "generate_exercise", {"topic": topic, "difficulty": "intermediate", "language": ctx.get("lang", "fr")}
        )
        yield from _emit_text(
            "J'ai généré un exercice pratique avec un corrigé chiffré vérifié. Ouvre le bloc ci-dessus, "
            "tente-le, puis demande-moi de corriger ta réponse ou d'expliquer une étape."
        )
        return

    # Default: grounded conceptual answer via real retrieval.
    query = _last_user_text(payload) or (ctx.get("concept") or ctx.get("pageTitle") or "finance de marché")
    yield from _tool_call_sequence(services, "rag_search", {"query": query, "top_k": 5})
    yield from _emit_text(
        "Voici ce que je trouve dans la bibliothèque sur ce point (sources ci-dessus). "
        "Mode hors-ligne actif (pas de clé OpenAI) : je m'appuie sur le RAG local et les calculs vérifiés. "
        "Pose-moi une question précise sur le concept de cette page, demande un exercice, ou dis "
        "« montre-moi la parité call-put » et je piloterai l'outil."
    )


# ---------------------------------------------------------------------------
# Public entry point — yields SSE strings.
# ---------------------------------------------------------------------------
def run_agui_stream(services: Services, payload: dict) -> Iterator[str]:
    thread_id = payload.get("threadId") or _new_id("thread")
    run_id = payload.get("runId") or _new_id("run")
    ctx = extract_page_context(payload)

    use_openai = (
        services.settings.llm_provider == "openai" and bool(services.settings.openai_api_key)
    )

    yield _sse({"type": "RunStarted", "threadId": thread_id, "runId": run_id, "timestamp": _now()})
    yield _sse({"type": "StateSnapshot", "snapshot": {"page": ctx, "runtime": "openai" if use_openai else "offline"}})

    try:
        runner = _run_openai_agent if use_openai else _run_offline_agent
        produced = False
        for event in runner(services, payload, ctx):
            produced = True
            yield _sse(event)
        if not produced:
            yield from (_sse(e) for e in _emit_text("Je n'ai pas pu produire de réponse. Reformule ta question ?"))
        yield _sse({"type": "RunFinished", "threadId": thread_id, "runId": run_id, "outcome": {"type": "success"}})
    except Exception as exc:  # pragma: no cover - defensive
        yield _sse({"type": "RunError", "message": str(exc), "code": "AGUI_RUN_ERROR"})
