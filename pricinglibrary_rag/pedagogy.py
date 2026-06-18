"""Pedagogical classification and scoring of source chunks.

This module turns a raw text chunk into structured pedagogical metadata so the
RAG corpus can actually drive serious course generation, not just retrieval.

It is deterministic and dependency-light (regex + heuristics, FR/EN), in line
with the project's local-first / offline-testable philosophy. No LLM call is
required to classify a chunk; the LLM only writes the final prose later.

Produced per chunk:
- content_type        primary pedagogical role (taxonomy below)
- content_types       every role detected (ordered by strength)
- contains_formula / _example / _exercise / _definition / _case_study
- difficulty_level    beginner | intermediate | advanced | expert
- pedagogical_value   0-100, usefulness to build a course
- quality_score       0-100, structural cleanliness (anti-OCR/anti-noise)
- usable_for_course   bool, gate for course generation
- keywords            clean top terms
- summary             short self-describing snippet

Aggregate helpers summarise a list of chunks and detect pedagogical gaps
(missing definitions / examples / exercises / formulas ...), which is what the
generator uses to flag holes instead of inventing content.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

from .text_utils import concise_snippet, keyword_scores, split_sentences, tokenize

# ---------------------------------------------------------------------------
# Taxonomy
# ---------------------------------------------------------------------------

CONTENT_TYPES: tuple[str, ...] = (
    "theory",
    "definition",
    "formula",
    "example",
    "worked_example",
    "exercise",
    "solution",
    "case_study",
    "historical_context",
    "market_context",
    "code",
    "table",
    "diagram_description",
    "methodology",
    "warning",
    "intuition",
    "summary",
)

# Canonical pedagogical flow a real lesson should be able to assemble. The
# generator compares what the sources actually contain against this and reports
# the missing pieces instead of hallucinating them.
PEDAGOGICAL_FLOW: tuple[str, ...] = (
    "definition",
    "intuition",
    "formula",
    "example",
    "worked_example",
    "exercise",
    "solution",
    "case_study",
    "summary",
)

# Content types that carry teachable substance (used for usability gating).
_SUBSTANTIVE_TYPES = {
    "definition",
    "formula",
    "example",
    "worked_example",
    "exercise",
    "solution",
    "case_study",
    "methodology",
    "intuition",
    "theory",
    "code",
}

# Structural noise: a chunk dominated by these is not course material.
_NON_TEACHING_TYPES = {"table", "historical_context"}


# ---------------------------------------------------------------------------
# Lexical cue banks (FR + EN). Lowercased substring / word cues.
# ---------------------------------------------------------------------------

_DEFINITION_CUES = (
    "is defined as", "we define", "is called", "refers to", "denotes",
    "definition", "by definition", "is known as", "that is, the",
    "se definit", "se définit", "on definit", "on définit", "on appelle",
    "est defini", "est défini", "designe", "désigne", "c'est-a-dire",
    "autrement dit", "par definition", "par définition", "appele", "appelé",
)

_EXAMPLE_CUES = (
    "for example", "for instance", "e.g.", "as an example", "consider a",
    "consider the", "suppose that", "imagine", "take the case",
    "par exemple", "prenons", "considerons", "considérons", "supposons",
    "a titre d'exemple", "exemple", "illustration", "to illustrate",
    "pour illustrer",
)

_EXERCISE_CUES = (
    "exercise", "problem set", "question", "compute the", "calculate the",
    "prove that", "show that", "find the", "determine the", "your task",
    "exercice", "calculer", "montrer que", "demontrer", "démontrer",
    "determiner", "déterminer", "a vous de", "à vous de", "travail demande",
    "questions:", "problem ", "tp ", "td ",
)

_SOLUTION_CUES = (
    "solution", "answer key", "answer:", "we have", "it follows that",
    "therefore", "hence", "thus we", "corrige", "corrigé", "correction",
    "reponse", "réponse", "on obtient", "il vient", "il s'ensuit",
    "proof.", "proof:", "demonstration", "démonstration", "q.e.d",
)

_CASE_STUDY_CUES = (
    "case study", "case:", "scenario", "real-world", "in practice the desk",
    "a trader", "the desk", "etude de cas", "étude de cas", "cas pratique",
    "mise en situation", "sur le desk", "un trader", "salle de marche",
    "salle de marché",
)

_HISTORY_CUES = (
    "in 19", "in 20", "history of", "historically", "founded", "century",
    "crisis of", "back in", "en 19", "en 20", "historiquement", "a l'epoque",
    "à l'époque", "fonde en", "fondé en",
)

_MARKET_CUES = (
    "bid", "ask", "spread", "market maker", "liquidity", "order book",
    "trading desk", "front office", "quote", "client", "broker", "screen",
    "bloomberg", "marche", "marché", "cotation", "teneur de marche",
)

_METHOD_CUES = (
    "step 1", "step 2", "first,", "second,", "then,", "finally,", "algorithm",
    "procedure", "the method", "approach is", "methodology", "we proceed",
    "etape 1", "étape 1", "methode", "méthode", "procedure", "procédure",
    "on procede", "on procède", "demarche", "démarche", "pseudocode",
)

_WARNING_CUES = (
    "note that", "be careful", "caution", "warning", "pitfall", "beware",
    "however, one must", "a common mistake", "do not", "should not",
    "attention", "remarque", "attention:", "piege", "piège", "erreur courante",
    "il ne faut pas", "prudence", "limite du modele", "limite du modèle",
)

_INTUITION_CUES = (
    "intuitively", "the intuition", "think of", "you can picture", "loosely",
    "in plain terms", "heuristically", "morally", "intuition", "intuitivement",
    "en clair", "pour faire simple", "image mentale", "on peut voir",
)

_SUMMARY_CUES = (
    "in summary", "to summarize", "to sum up", "in conclusion", "key takeaways",
    "takeaway", "recap", "en resume", "en résumé", "pour resumer", "pour résumer",
    "en conclusion", "a retenir", "à retenir", "points cles", "points clés",
    "synthese", "synthèse",
)

_DIAGRAM_CUES = (
    "figure", "see figure", "the diagram", "the chart", "as shown in",
    "plotted", "the graph below", "x-axis", "y-axis", "schema", "schéma",
    "graphique", "le diagramme", "voir figure", "courbe ci-dessous",
)

# Vocabulary used to estimate difficulty.
_ADVANCED_TERMS = (
    "stochastic", "martingale", "girsanov", "radon-nikodym", "ito", "itô",
    "sde", "measure change", "feynman-kac", "pde", "quadratic variation",
    "filtration", "semimartingale", "levy", "lévy", "copula", "saddlepoint",
    "characteristic function", "fourier", "malliavin", "hjm", "lmm",
)
_INTERMEDIATE_TERMS = (
    "black-scholes", "duration", "convexity", "dv01", "greeks", "implied vol",
    "bootstrapping", "monte carlo", "var", "cs01", "barrier", "autocall",
    "hedge", "delta", "gamma", "vega", "discount factor", "par rate",
)
_BEGINNER_TERMS = (
    "what is", "introduction", "basics", "simply put", "in this chapter we",
    "definition", "for beginners", "elementary", "introduction a",
    "introduction à", "les bases", "premiers pas",
)


# ---------------------------------------------------------------------------
# Regex signals
# ---------------------------------------------------------------------------

# Math / formula signals.
_LATEX_RE = re.compile(r"\\(?:frac|sqrt|sum|int|partial|sigma|mu|alpha|beta|delta|cdot|times|left|right|begin\{)")
_MATH_OP_RE = re.compile(r"[=≈≤≥±×÷√∫∑∂∞≠→∈∀∃]")
_GREEK_RE = re.compile(r"[α-ωΑ-Ω]")
_EQUATION_RE = re.compile(r"[A-Za-z0-9\)\]]\s*[=≈]\s*[-+(]?\s*[A-Za-z0-9\\(]")
_SUPERSCRIPT_RE = re.compile(r"[A-Za-z0-9]\^[0-9({]|[²³√]")

# Code signals.
_CODE_RE = re.compile(
    r"```|def\s+\w+\s*\(|import\s+\w+|for\s*\(|while\s*\(|#include|"
    r"println|System\.out|std::|=>|\bnp\.\w+|\bplt\.\w+|return\s+\w+;|\{\s*$",
    re.MULTILINE,
)

# Table signals: pipe tables or many aligned numeric columns.
_PIPE_TABLE_RE = re.compile(r"^\s*\|?[^|\n]*\|[^|\n]*\|", re.MULTILINE)

_NUMBER_RE = re.compile(r"(?<![\w.])-?\d+(?:[.,]\d+)?%?")

# A numeric result being computed (e.g. "= 4.21", "payoff = 100,000", "we obtain").
_RESULT_RE = re.compile(
    r"=\s*[-+(]?\s*\d|\b(we (?:get|obtain|find|have)|results? in|gives? (?:us|a)|"
    r"on (?:obtient|trouve)|il vient|equals|yields)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ChunkPedagogy:
    content_type: str
    content_types: list[str]
    contains_formula: bool
    contains_example: bool
    contains_exercise: bool
    contains_definition: bool
    contains_case_study: bool
    difficulty_level: str
    pedagogical_value: int
    quality_score: int
    usable_for_course: bool
    keywords: list[str] = field(default_factory=list)
    summary: str = ""

    def to_metadata(self) -> dict:
        """Compact dict stored inside chunk metadata_json under "pedagogy"."""
        return {
            "content_type": self.content_type,
            "content_types": self.content_types,
            "contains_formula": self.contains_formula,
            "contains_example": self.contains_example,
            "contains_exercise": self.contains_exercise,
            "contains_definition": self.contains_definition,
            "contains_case_study": self.contains_case_study,
            "difficulty_level": self.difficulty_level,
            "pedagogical_value": self.pedagogical_value,
            "quality_score": self.quality_score,
            "usable_for_course": self.usable_for_course,
            "summary": self.summary,
        }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def classify_chunk(text: str, *, section_title: str | None = None) -> ChunkPedagogy:
    """Classify and score a single chunk of source text."""

    raw = text or ""
    stripped = raw.strip()
    lower = stripped.lower()
    tokens = tokenize(stripped)
    token_count = len(tokens)

    quality = _structural_quality(stripped, tokens)
    type_scores, flags = _content_type_scores(stripped, lower, tokens)

    contains_definition = flags["definition"]
    contains_example = flags["example"]
    contains_exercise = flags["exercise"]
    contains_case_study = flags["case_study"]
    contains_formula = flags["formula"]

    ordered = [t for t, s in sorted(type_scores.items(), key=lambda kv: kv[1], reverse=True) if s > 0]
    primary = ordered[0] if ordered else "theory"

    difficulty = _difficulty(lower)
    ped_value = _pedagogical_value(
        type_scores=type_scores,
        flags=flags,
        quality=quality,
        token_count=token_count,
        stripped=stripped,
    )
    usable = _is_usable(
        primary=primary,
        ped_value=ped_value,
        quality=quality,
        token_count=token_count,
        type_scores=type_scores,
    )
    keywords = [term for term, _ in keyword_scores([stripped], top_k=10)]
    summary = concise_snippet(stripped, max_chars=200)

    return ChunkPedagogy(
        content_type=primary,
        content_types=ordered[:5] or ["theory"],
        contains_formula=contains_formula,
        contains_example=contains_example,
        contains_exercise=contains_exercise,
        contains_definition=contains_definition,
        contains_case_study=contains_case_study,
        difficulty_level=difficulty,
        pedagogical_value=ped_value,
        quality_score=quality,
        usable_for_course=usable,
        keywords=keywords,
        summary=summary,
    )


# ---------------------------------------------------------------------------
# Document-level theme / subtheme inference
# ---------------------------------------------------------------------------

# theme -> (asset_class, cue terms). Order matters: first strong match wins for
# subtheme, but the theme is chosen by highest weighted score.
_THEME_BANK: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("Rates & Fixed Income", "rates", (
        "interest rate", "swap", "bond", "duration", "convexity", "yield curve",
        "discount factor", "dv01", "libor", "sofr", "fixed income", "zero coupon",
        "forward rate", "bootstrapping", "treasury", "coupon",
    )),
    ("Derivatives & Volatility", "equity_derivatives", (
        "option", "volatility", "implied vol", "smile", "skew", "barrier",
        "greeks", "black-scholes", "black scholes", "delta", "gamma", "vega",
        "exotic", "autocall", "vanilla", "payoff", "straddle",
    )),
    ("Credit & XVA", "credit", (
        "credit", "cds", "default", "xva", "cva", "counterparty", "spread",
        "recovery", "hazard rate", "credit risk", "risky annuity",
    )),
    ("Risk Management", "multi_asset", (
        "value at risk", "var", "expected shortfall", "stress test", "risk limit",
        "basel", "regulatory capital", "market risk", "risk management",
        "backtesting", "drawdown",
    )),
    ("Quant Methods & Pricing", "multi_asset", (
        "monte carlo", "simulation", "finite difference", "pde", "numerical",
        "stochastic calculus", "ito", "girsanov", "variance reduction",
        "discretization", "lattice", "binomial tree",
    )),
    ("Trading & Markets", "multi_asset", (
        "trading", "execution", "algorithmic", "market microstructure", "order book",
        "systematic", "backtest", "strategy", "portfolio", "market maker",
    )),
    ("Foundations & Math", "multi_asset", (
        "probability", "statistics", "linear algebra", "calculus", "mathematics",
        "distribution", "stochastic process", "measure theory", "expectation",
    )),
)


def infer_document_theme(text: str, title: str | None = None) -> dict:
    """Infer a coarse theme/subtheme/asset_class for a whole document.

    Title cues are weighted 3x because the file/document title is the strongest
    available signal on this corpus (chunks otherwise share generic metadata).
    """
    title_l = (title or "").lower()
    body_l = (text or "")[:8000].lower()

    best_theme = "Market Finance Core"
    best_asset = "multi_asset"
    best_score = 0.0
    best_subtheme: str | None = None

    for theme, asset_class, cues in _THEME_BANK:
        score = 0.0
        local_best_cue: str | None = None
        local_best_cue_score = 0.0
        for cue in cues:
            hits = body_l.count(cue) + 3 * title_l.count(cue)
            if hits:
                score += hits
                if hits > local_best_cue_score:
                    local_best_cue_score = hits
                    local_best_cue = cue
        if score > best_score:
            best_score = score
            best_theme = theme
            best_asset = asset_class
            best_subtheme = local_best_cue

    return {
        "theme": best_theme,
        "subtheme": best_subtheme,
        "asset_class": best_asset if best_score > 0 else "multi_asset",
        "theme_confidence": int(min(best_score, 100)),
    }


def pedagogy_from_metadata(metadata: dict | None) -> dict | None:
    """Read back the persisted pedagogy block, if present."""
    if not metadata:
        return None
    pedagogy = metadata.get("pedagogy")
    return pedagogy if isinstance(pedagogy, dict) else None


# ---------------------------------------------------------------------------
# Aggregation + gap detection
# ---------------------------------------------------------------------------


def summarize_pedagogy(items: Iterable[dict]) -> dict:
    """Aggregate pedagogy dicts into a corpus/selection report."""
    items = [it for it in items if isinstance(it, dict)]
    total = len(items)
    if not total:
        return {
            "total": 0,
            "usable": 0,
            "usable_ratio": 0.0,
            "average_pedagogical_value": 0.0,
            "average_quality_score": 0.0,
            "content_type_distribution": {},
            "difficulty_distribution": {},
            "definitions": 0,
            "examples": 0,
            "exercises": 0,
            "formulas": 0,
            "case_studies": 0,
        }

    type_dist: dict[str, int] = {}
    diff_dist: dict[str, int] = {}
    usable = 0
    ped_sum = 0.0
    qual_sum = 0.0
    defs = ex = exo = formulas = cases = 0
    for it in items:
        ct = str(it.get("content_type", "theory"))
        type_dist[ct] = type_dist.get(ct, 0) + 1
        dl = str(it.get("difficulty_level", "intermediate"))
        diff_dist[dl] = diff_dist.get(dl, 0) + 1
        usable += 1 if it.get("usable_for_course") else 0
        ped_sum += float(it.get("pedagogical_value", 0) or 0)
        qual_sum += float(it.get("quality_score", 0) or 0)
        defs += 1 if it.get("contains_definition") else 0
        ex += 1 if it.get("contains_example") else 0
        exo += 1 if it.get("contains_exercise") else 0
        formulas += 1 if it.get("contains_formula") else 0
        cases += 1 if it.get("contains_case_study") else 0

    return {
        "total": total,
        "usable": usable,
        "usable_ratio": round(usable / total, 4),
        "average_pedagogical_value": round(ped_sum / total, 2),
        "average_quality_score": round(qual_sum / total, 2),
        "content_type_distribution": dict(sorted(type_dist.items(), key=lambda kv: kv[1], reverse=True)),
        "difficulty_distribution": diff_dist,
        "definitions": defs,
        "examples": ex,
        "exercises": exo,
        "formulas": formulas,
        "case_studies": cases,
    }


_STAGE_FLAG = {
    "definition": "contains_definition",
    "formula": "contains_formula",
    "example": "contains_example",
    "exercise": "contains_exercise",
    "case_study": "contains_case_study",
}


def stage_covered(pedagogy: dict, stage: str) -> bool:
    """Does a single chunk's pedagogy cover a given lesson-flow stage?"""
    if not isinstance(pedagogy, dict):
        return False
    flag = _STAGE_FLAG.get(stage)
    if flag and pedagogy.get(flag):
        return True
    if pedagogy.get("content_type") == stage:
        return True
    return stage in (pedagogy.get("content_types") or [])


def detect_pedagogical_gaps(items: Iterable[dict]) -> dict:
    """Compare available content types against the canonical lesson flow.

    Returns which flow stages are present, which are missing, and a readable
    usability verdict. This is what lets the generator flag holes instead of
    inventing content.
    """
    items = [it for it in items if isinstance(it, dict)]
    present: set[str] = set()
    for it in items:
        for ct in it.get("content_types", []) or [it.get("content_type")]:
            if ct:
                present.add(str(ct))
        # boolean flags are an extra safety net
        if it.get("contains_definition"):
            present.add("definition")
        if it.get("contains_example"):
            present.add("example")
        if it.get("contains_exercise"):
            present.add("exercise")
        if it.get("contains_formula"):
            present.add("formula")
        if it.get("contains_case_study"):
            present.add("case_study")

    present_flow = [stage for stage in PEDAGOGICAL_FLOW if stage in present]
    missing_flow = [stage for stage in PEDAGOGICAL_FLOW if stage not in present]

    # Core stages a serious course really needs.
    core = {"definition", "formula", "example"}
    missing_core = [stage for stage in core if stage not in present]

    if not items:
        status = "not_usable"
    elif not missing_core:
        status = "usable"
    elif len(missing_core) < len(core):
        status = "partially_usable"
    else:
        status = "not_usable"

    return {
        "present": present_flow,
        "missing": missing_flow,
        "missing_core": missing_core,
        "status": status,
    }


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _count_cues(lower: str, cues: tuple[str, ...]) -> int:
    return sum(1 for cue in cues if cue in lower)


def _content_type_scores(
    stripped: str, lower: str, tokens: list[str]
) -> tuple[dict[str, float], dict[str, bool]]:
    """Return (dominance_scores, presence_flags).

    Two distinct outputs on purpose:
    - presence flags answer "does this chunk CONTAIN a formula/example/...?"
      (permissive: one real occurrence is enough);
    - dominance scores answer "what IS this chunk mostly about?" and decide the
      primary content_type (density-aware, so a prose paragraph that happens to
      hold one equation stays theory/definition, not formula).
    All dominance scores are bounded to roughly [0, 5] so families compete fairly.
    """
    scores: dict[str, float] = {}
    length = max(len(stripped), 1)
    n_tokens = len(tokens)
    blocks = max(length / 500.0, 1.0)  # ~number of 500-char blocks

    # --- math signals ------------------------------------------------------
    math_chars = len(_MATH_OP_RE.findall(stripped)) + len(_GREEK_RE.findall(stripped))
    equations = len(_EQUATION_RE.findall(stripped))
    latex = len(_LATEX_RE.findall(stripped))
    superscripts = len(_SUPERSCRIPT_RE.findall(stripped))
    math_char_ratio = math_chars / length
    formula_density = (equations + 2 * latex + superscripts) / blocks

    # presence: a single genuine equation / latex command is enough
    contains_formula = equations >= 1 or latex >= 1 or (math_chars >= 6 and superscripts >= 1)
    # dominance: only when math is actually dense relative to length
    if (formula_density >= 1.2 or math_char_ratio >= 0.03) and (equations + latex) >= 2:
        scores["formula"] = min(formula_density, 5.0)

    # --- code --------------------------------------------------------------
    code_hits = len(_CODE_RE.findall(stripped))
    if code_hits >= 2:
        scores["code"] = min(1.5 + code_hits / 2.0, 5.0)

    # --- table -------------------------------------------------------------
    pipe_rows = len(_PIPE_TABLE_RE.findall(stripped))
    numbers = len(_NUMBER_RE.findall(stripped))
    digit_ratio = sum(ch.isdigit() for ch in stripped) / length
    if pipe_rows >= 2:
        scores["table"] = min(1.5 + pipe_rows / 3.0, 5.0)
    elif digit_ratio > 0.22 and numbers >= 16:
        scores["table"] = min(digit_ratio * 8, 4.0)

    # --- lexical cue families (dominance ~ cue density, bounded) -----------
    def add(name: str, cues: tuple[str, ...], weight: float = 1.0, cap: float = 4.0) -> int:
        hits = _count_cues(lower, cues)
        if hits:
            scores[name] = min(scores.get(name, 0.0) + hits * weight, cap)
        return hits

    n_definition = add("definition", _DEFINITION_CUES, 1.3)
    n_example = add("example", _EXAMPLE_CUES, 1.1)
    n_exercise = add("exercise", _EXERCISE_CUES, 1.2)
    n_solution = add("solution", _SOLUTION_CUES, 0.9)
    n_case = add("case_study", _CASE_STUDY_CUES, 1.1)
    add("historical_context", _HISTORY_CUES, 0.7, cap=3.0)
    add("market_context", _MARKET_CUES, 0.4, cap=2.5)
    n_method = add("methodology", _METHOD_CUES, 0.9)
    add("warning", _WARNING_CUES, 0.9, cap=3.0)
    add("intuition", _INTUITION_CUES, 1.1)
    add("summary", _SUMMARY_CUES, 1.1)
    add("diagram_description", _DIAGRAM_CUES, 0.7, cap=2.5)

    # --- imperative / interrogative cue for genuine exercises --------------
    has_imperative = bool(
        re.search(
            r"(?i)\b(compute|calculate|prove|show that|find the|determine|derive|"
            r"calculer|montrer que|determiner|déterminer|demontrer|démontrer|estimer)\b",
            stripped,
        )
    )
    if n_exercise and not has_imperative and "?" not in stripped:
        # word "problem"/"question" alone is weak; damp dominance
        scores["exercise"] = scores.get("exercise", 0.0) * 0.5
    contains_exercise = bool(n_exercise and (has_imperative or "?" in stripped))

    # --- worked_example: a concrete example that is actually computed -------
    # Needs an example cue, enough numbers, a real computation/result signal,
    # AND maths or a solution feel. "method + numbers" alone is not a worked
    # example (that is just methodology with figures), which prevents the type
    # from swallowing every numeric paragraph.
    has_result = bool(_RESULT_RE.search(stripped))
    contains_worked = bool(
        n_example and numbers >= 6 and has_result and (equations >= 1 or n_solution)
    )
    if contains_worked:
        # Bounded so it competes fairly with theory/definition rather than
        # always outranking them.
        scores["worked_example"] = min(2.2 + min(numbers / 12.0, 1.5), 4.0)

    # --- theory: conceptual prose fallback / baseline ----------------------
    sentences = split_sentences(stripped)
    alpha_ratio = sum(ch.isalpha() for ch in stripped) / length
    if n_tokens >= 50 and len(sentences) >= 3 and alpha_ratio > 0.58:
        scores["theory"] = min(1.2 + n_tokens / 400.0, 3.0)

    scores = {k: v for k, v in scores.items() if v > 0}

    flags = {
        "definition": bool(n_definition),
        "example": bool(n_example or contains_worked),
        "exercise": contains_exercise,
        "case_study": bool(n_case),
        "formula": contains_formula,
    }
    return scores, flags


def _difficulty(lower: str) -> str:
    adv = _count_cues(lower, _ADVANCED_TERMS)
    inter = _count_cues(lower, _INTERMEDIATE_TERMS)
    beg = _count_cues(lower, _BEGINNER_TERMS)
    if adv >= 2 or (adv >= 1 and "proof" in lower):
        return "expert" if adv >= 3 else "advanced"
    if inter >= 1 and adv == 0:
        return "intermediate"
    if beg >= 1 and inter == 0 and adv == 0:
        return "beginner"
    if adv >= 1:
        return "advanced"
    return "intermediate"


def _structural_quality(stripped: str, tokens: list[str]) -> int:
    """Structural cleanliness 0-100 (anti-OCR / anti-TOC / anti-bibliography)."""
    if not stripped:
        return 0
    token_count = len(tokens)
    if token_count < 20:
        return 12

    lines = [ln.strip() for ln in stripped.splitlines() if ln.strip()]
    avg_line_len = sum(len(ln) for ln in lines) / max(len(lines), 1)
    short_line_ratio = sum(1 for ln in lines if len(ln) < 34) / max(len(lines), 1)
    sentence_like = len(re.findall(r"[.!?]\s+[A-Z0-9]", stripped))
    length = max(len(stripped), 1)
    alpha_ratio = sum(ch.isalpha() for ch in stripped) / length
    digit_ratio = sum(ch.isdigit() for ch in stripped) / length
    lower = stripped.lower()

    score = 1.0
    if avg_line_len < 42 and short_line_ratio > 0.45:
        score *= 0.45
    if sentence_like < 2 and token_count < 140:
        score *= 0.6
    if alpha_ratio < 0.45:
        score *= 0.5
    if digit_ratio > 0.30:
        score *= 0.6
    if "table of contents" in lower[:300] or lower[:60].strip().startswith("contents"):
        score *= 0.3
    if "bibliography" in lower[:200] or "references" == lower[:10].strip():
        score *= 0.4
    # dense citation/reference noise: many "et al" / bracketed refs
    if lower.count("et al") >= 3 or len(re.findall(r"\[\d+\]", stripped)) >= 6:
        score *= 0.55
    return int(round(max(0.05, min(score, 1.0)) * 100))


def _pedagogical_value(
    *,
    type_scores: dict[str, float],
    flags: dict[str, bool],
    quality: int,
    token_count: int,
    stripped: str,
) -> int:
    """0-100 usefulness for building a course."""
    if token_count < 20:
        return 5

    value = 34.0  # base for clean prose

    # conceptual richness (presence-based: flags + dominance signals)
    if flags.get("definition"):
        value += 16
    if flags.get("formula"):
        value += 12
    if flags.get("example"):
        value += 14
    if type_scores.get("worked_example"):
        value += 8
    if flags.get("exercise"):
        value += 12
    if type_scores.get("solution"):
        value += 8
    if flags.get("case_study"):
        value += 10
    if type_scores.get("intuition"):
        value += 8
    if type_scores.get("methodology"):
        value += 6
    if type_scores.get("summary"):
        value += 4

    # combo bonus: self-sufficient teaching unit
    combo = sum(
        1
        for present in (
            flags.get("definition"),
            flags.get("formula"),
            flags.get("example"),
            type_scores.get("worked_example"),
            type_scores.get("intuition"),
        )
        if present
    )
    if combo >= 3:
        value += 10

    # penalties for non-teaching dominance
    if type_scores.get("table") and len(type_scores) == 1:
        value -= 25
    if type_scores.get("historical_context") and not any(
        type_scores.get(k) for k in _SUBSTANTIVE_TYPES
    ):
        value -= 15

    # length sweet spot
    if token_count < 40:
        value -= 10
    elif token_count < 80:
        value -= 4
    elif token_count > 120:
        value += 4

    # quality gate: noisy text cannot teach
    value *= quality / 100.0 * 0.6 + 0.4

    return int(round(max(0.0, min(value, 100.0))))


def _is_usable(
    *,
    primary: str,
    ped_value: int,
    quality: int,
    token_count: int,
    type_scores: dict[str, float],
) -> bool:
    if token_count < 40:
        return False
    if quality < 35:
        return False
    if ped_value < 35:
        return False
    if primary in _NON_TEACHING_TYPES and not any(
        type_scores.get(k) for k in _SUBSTANTIVE_TYPES
    ):
        return False
    return True
