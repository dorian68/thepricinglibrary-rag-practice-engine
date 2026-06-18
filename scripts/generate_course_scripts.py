from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from pricinglibrary_rag.factory import build_services
from pricinglibrary_rag.practice_agent import PracticeAgent
from pricinglibrary_rag.schemas import CourseRequest, DocumentMetadata


@dataclass(frozen=True)
class CourseSpec:
    slug: str
    topic: str
    product: str | None
    concepts: list[str] = field(default_factory=list)
    level: str = "intermediate"
    duration_minutes: int = 120
    module_count: int = 5


COURSE_SPECS = [
    CourseSpec(
        slug="vanilla-options-quote",
        topic="Vanilla options desk quote",
        product="equity vanilla option",
        concepts=["Black-Scholes", "put-call parity", "delta", "vega"],
        level="beginner",
        duration_minutes=90,
        module_count=4,
    ),
    CourseSpec(
        slug="options-book-greeks-pnl",
        topic="Options book Greeks and P&L attribution",
        product="equity options book",
        concepts=["delta", "gamma", "vega", "theta", "hedging"],
        level="intermediate",
        duration_minutes=120,
        module_count=5,
    ),
    CourseSpec(
        slug="rates-swaps-dv01",
        topic="Interest-rate swaps, PV and DV01",
        product="EUR interest-rate swap",
        concepts=["par rate", "annuity", "DV01", "curve shock"],
        level="intermediate",
        duration_minutes=120,
        module_count=5,
    ),
    CourseSpec(
        slug="yield-curve-bootstrapping",
        topic="Yield curve bootstrapping for desk pricing",
        product="interest-rate curve",
        concepts=["discount factors", "zero curve", "forward rates", "interpolation"],
        level="intermediate",
        duration_minutes=130,
        module_count=5,
    ),
    CourseSpec(
        slug="implied-volatility-smile",
        topic="Implied volatility smile and quote cleaning",
        product="equity index options",
        concepts=["implied volatility", "smile", "skew", "SVI"],
        level="intermediate",
        duration_minutes=130,
        module_count=5,
    ),
    CourseSpec(
        slug="monte-carlo-pricing",
        topic="Monte Carlo pricing and confidence intervals",
        product="path-dependent option",
        concepts=["GBM", "Asian option", "standard error", "variance reduction"],
        level="advanced",
        duration_minutes=140,
        module_count=5,
    ),
    CourseSpec(
        slug="barrier-options-gap-risk",
        topic="Barrier options and gap risk",
        product="FX barrier option",
        concepts=["down-and-out", "knock-out", "gap risk", "monitoring"],
        level="advanced",
        duration_minutes=130,
        module_count=5,
    ),
    CourseSpec(
        slug="structured-products-autocall",
        topic="Autocallable structured products from term sheet to scenario table",
        product="autocallable note",
        concepts=["coupon barrier", "autocall", "protection barrier", "redemption"],
        level="advanced",
        duration_minutes=150,
        module_count=6,
    ),
    CourseSpec(
        slug="credit-derivatives-cds",
        topic="CDS spread risk, carry and CS01",
        product="single-name CDS",
        concepts=["spread", "risky annuity", "CS01", "carry"],
        level="intermediate",
        duration_minutes=110,
        module_count=4,
    ),
    CourseSpec(
        slug="market-risk-var-stress",
        topic="Market risk VaR, stress testing and escalation",
        product="multi-asset portfolio",
        concepts=["parametric VaR", "expected shortfall", "stress test", "risk limit"],
        level="intermediate",
        duration_minutes=120,
        module_count=5,
    ),
    CourseSpec(
        slug="fixed-income-bonds-duration",
        topic="Bond pricing, duration and rate-shock P&L",
        product="fixed-income bond",
        concepts=["clean price", "YTM", "duration", "convexity", "DV01"],
        level="beginner",
        duration_minutes=100,
        module_count=4,
    ),
    CourseSpec(
        slug="stochastic-calculus-for-hedging",
        topic="Stochastic calculus only where it helps hedging",
        product="option pricing model",
        concepts=["Ito lemma", "SDE", "risk-neutral measure", "hedging"],
        level="expert",
        duration_minutes=150,
        module_count=6,
    ),
]

FORMULA_BANK = {
    "vanilla-options-quote": [
        (
            "Black-Scholes call with dividend yield",
            r"C = S_0 e^{-qT}N(d_1)-K e^{-rT}N(d_2)",
            "quote the option premium from observable inputs and document the carry assumptions.",
        ),
        (
            "d1/d2 controls",
            r"d_1=\frac{\ln(S_0/K)+(r-q+\frac{1}{2}\sigma^2)T}{\sigma\sqrt{T}},\qquad d_2=d_1-\sigma\sqrt{T}",
            "check moneyness, time and volatility before trusting the model output.",
        ),
        (
            "Put-call parity",
            r"C-P=S_0e^{-qT}-Ke^{-rT}",
            "detect stale quotes or inconsistent funding/dividend assumptions.",
        ),
    ],
    "options-book-greeks-pnl": [
        (
            "Delta-gamma-vega-theta attribution",
            r"\Delta V \approx \Delta\,\Delta S+\frac{1}{2}\Gamma(\Delta S)^2+\nu\,\Delta\sigma+\Theta\,\Delta t",
            "break a daily P&L move into explainable risk buckets.",
        ),
        (
            "Delta hedge notional",
            r"\text{Shares to trade}=-N_{\text{contracts}}\times m\times \Delta_{\text{option}}",
            "translate model delta into a concrete hedge ticket.",
        ),
        (
            "Residual gamma P&L",
            r"\text{Gamma P\&L}\approx \frac{1}{2}\Gamma(\Delta S)^2",
            "show why a delta-neutral book can still win or lose on realized moves.",
        ),
    ],
    "rates-swaps-dv01": [
        (
            "Par swap rate",
            r"R_{\text{par}}=\frac{P(0,T_0)-P(0,T_n)}{\sum_{i=1}^{n}\alpha_i P(0,T_i)}",
            "turn a discount curve into the fixed rate that prices the swap at par.",
        ),
        (
            "Swap PV around par",
            r"\text{PV}\approx N\,(R_{\text{par}}-K)\sum_{i=1}^{n}\alpha_i P(0,T_i)",
            "explain the sign of a receiver or payer swap after a rate move.",
        ),
        (
            "DV01",
            r"\text{DV01}=N\times A\times 10^{-4},\qquad A=\sum_{i=1}^{n}\alpha_i P(0,T_i)",
            "convert a one basis point shock into currency P&L.",
        ),
    ],
    "yield-curve-bootstrapping": [
        (
            "Discount factor recursion",
            r"P(0,T_n)=\frac{1-c_n\sum_{i=1}^{n-1}\alpha_iP(0,T_i)}{1+c_n\alpha_n}",
            "bootstrap the next point of the curve from a quoted par instrument.",
        ),
        (
            "Zero rate",
            r"z(0,T)=-\frac{\ln P(0,T)}{T}",
            "convert discount factors into continuously compounded zero rates.",
        ),
        (
            "Forward rate",
            r"f(t_i,t_j)=\frac{1}{t_j-t_i}\ln\left(\frac{P(0,t_i)}{P(0,t_j)}\right)",
            "read the market-implied carry between two maturities.",
        ),
    ],
    "implied-volatility-smile": [
        (
            "Implied volatility root",
            r"\sigma_{\text{imp}}:\quad BS(S,K,r,q,T,\sigma_{\text{imp}})=P_{\text{mkt}}",
            "convert option prices into comparable volatility quotes.",
        ),
        (
            "Newton update",
            r"\sigma_{k+1}=\sigma_k-\frac{BS(\sigma_k)-P_{\text{mkt}}}{\text{Vega}(\sigma_k)}",
            "iterate quickly while monitoring low-vega strikes.",
        ),
        (
            "SVI total variance",
            r"w(k)=a+b\left(\rho(k-m)+\sqrt{(k-m)^2+\eta^2}\right)",
            "fit a clean smile while keeping skew and curvature visible.",
        ),
    ],
    "monte-carlo-pricing": [
        (
            "GBM step",
            r"S_{t+\Delta t}=S_t\exp\left((r-q-\frac{1}{2}\sigma^2)\Delta t+\sigma\sqrt{\Delta t}Z\right)",
            "simulate risk-neutral paths for a path-dependent payoff.",
        ),
        (
            "Discounted estimator",
            r"\hat{V}_0=e^{-rT}\frac{1}{M}\sum_{m=1}^{M}\Phi(S^{(m)})",
            "price by averaging simulated payoffs and discounting them.",
        ),
        (
            "Confidence interval",
            r"\hat{V}_0 \pm 1.96\frac{s_{\Phi}}{\sqrt{M}}",
            "decide whether the Monte Carlo error is small enough for the desk use case.",
        ),
    ],
    "barrier-options-gap-risk": [
        (
            "Down-and-out call payoff",
            r"\Phi=(S_T-K)^+\mathbf{1}_{\min_{0\leq t\leq T}S_t>H}",
            "make the path condition explicit before discussing price.",
        ),
        (
            "Barrier gap loss",
            r"\text{Gap loss}\approx \Delta_{\text{pre-hit}}\,(S_{\text{hit}}-S_{\text{next}})",
            "estimate the residual risk when the hedge cannot be rebalanced at the barrier.",
        ),
        (
            "Discrete monitoring adjustment",
            r"H_{\text{eff}}\approx H\exp(\pm\beta\sigma\sqrt{\Delta t}),\qquad \beta\approx0.5826",
            "avoid mixing continuous-barrier prices with discretely monitored risk.",
        ),
    ],
    "structured-products-autocall": [
        (
            "Autocall redemption event",
            r"\mathbf{1}_{\text{call},i}=\mathbf{1}_{S_{t_i}\geq B_{\text{call}}S_0}",
            "turn term-sheet language into scenario-table logic.",
        ),
        (
            "Coupon event",
            r"\text{Coupon}_i=Nc_i\mathbf{1}_{S_{t_i}\geq B_{\text{coupon}}S_0}",
            "separate income trigger risk from capital protection risk.",
        ),
        (
            "Protected redemption",
            r"\text{Redemption}=N\left[1-\max\left(0,1-\frac{S_T}{S_0}\right)\mathbf{1}_{S_T<B_{\text{prot}}S_0}\right]",
            "explain downside exposure to a non-quant stakeholder.",
        ),
    ],
    "credit-derivatives-cds": [
        (
            "Risky annuity",
            r"A=\sum_i \alpha_i\,DF_i\,Q(\tau>t_i)",
            "measure the present value of one spread point on the premium leg.",
        ),
        (
            "CS01",
            r"\text{CS01}=N\times A\times 10^{-4}",
            "convert a one basis point spread shock into currency P&L.",
        ),
        (
            "Spread P&L approximation",
            r"\Delta V\approx \text{CS01}\times \Delta s_{\text{bp}}",
            "explain the first-order impact of spread widening or tightening.",
        ),
    ],
    "market-risk-var-stress": [
        (
            "Parametric VaR",
            r"\text{VaR}_{\alpha}=V\,\sigma\,z_{\alpha}\sqrt{h}",
            "estimate the loss threshold for a linear book under normal assumptions.",
        ),
        (
            "Expected shortfall",
            r"\text{ES}_{\alpha}=V\,\sigma\sqrt{h}\frac{\phi(z_{\alpha})}{1-\alpha}",
            "look beyond the VaR quantile and quantify tail severity.",
        ),
        (
            "Stress P&L",
            r"\Delta V_{\text{stress}}=\sum_i \text{sensitivity}_i\times \Delta x_i",
            "translate a risk scenario into an escalation-ready loss estimate.",
        ),
    ],
    "fixed-income-bonds-duration": [
        (
            "Bond price",
            r"P=\sum_{i=1}^{n}\frac{CF_i}{(1+y)^{t_i}}",
            "turn cash flows and yield into clean price controls.",
        ),
        (
            "Modified duration",
            r"D_{\text{mod}}=\frac{D_{\text{Mac}}}{1+y/m}",
            "estimate price sensitivity to a parallel yield move.",
        ),
        (
            "Duration-convexity P&L",
            r"\frac{\Delta P}{P}\approx -D_{\text{mod}}\Delta y+\frac{1}{2}C(\Delta y)^2",
            "explain why convexity matters for larger rate shocks.",
        ),
    ],
    "stochastic-calculus-for-hedging": [
        (
            "Ito process",
            r"dS_t=\mu S_t\,dt+\sigma S_t\,dW_t",
            "state the modeling assumption behind the hedge derivation.",
        ),
        (
            "Ito lemma",
            r"dV=\left(\frac{\partial V}{\partial t}+\mu S\frac{\partial V}{\partial S}+\frac{1}{2}\sigma^2S^2\frac{\partial^2V}{\partial S^2}\right)dt+\sigma S\frac{\partial V}{\partial S}dW_t",
            "connect model dynamics to delta and gamma risk.",
        ),
        (
            "Risk-neutral drift",
            r"dS_t=(r-q)S_t\,dt+\sigma S_t\,dW_t^{\mathbb{Q}}",
            "separate pricing measure logic from real-world forecasting.",
        ),
    ],
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate practice-first course scripts for ThePricingLibrary from "
            "the local RAG corpus."
        )
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "generated" / "course_scripts"),
    )
    parser.add_argument(
        "--corpus-root",
        action="append",
        default=[],
        help="Folder containing PDFs/TXT/MD to ingest before generation. Can be repeated.",
    )
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Ingest corpus roots before generating. Off by default because ingestion is heavy.",
    )
    parser.add_argument("--force-ingest", action="store_true")
    parser.add_argument(
        "--llm-provider",
        choices=["template", "openai", "ollama", "transformers"],
        default=None,
        help="Override TPL_LLM_PROVIDER for this run.",
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--language", choices=["fr", "en"], default="fr")
    args = parser.parse_args()

    if args.llm_provider:
        os.environ["TPL_LLM_PROVIDER"] = args.llm_provider

    services = build_services()
    if args.ingest:
        roots = list(_resolve_corpus_roots(args.corpus_root))
        _ingest_roots(services, roots, force=args.force_ingest)
        services.retriever.refresh()

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    agent = PracticeAgent(services.generator)
    specs = COURSE_SPECS[: args.limit] if args.limit else COURSE_SPECS
    documents = services.store.list_documents(limit=10_000)

    index = {
        "generated_at": _now_label(),
        "llm": services.llm.name,
        "db_path": str(services.settings.db_path),
        "document_count": len(documents),
        "courses": [],
    }

    for spec in specs:
        request = CourseRequest(
            topic=spec.topic,
            product=spec.product,
            concepts=spec.concepts,
            level=spec.level,  # type: ignore[arg-type]
            duration_minutes=spec.duration_minutes,
            module_count=spec.module_count,
            language=args.language,
        )
        response = agent.create_course(request)
        markdown = _course_markdown(spec, response)
        path = output_dir / f"{spec.slug}.md"
        path.write_text(markdown, encoding="utf-8")
        index["courses"].append(
            {
                "slug": spec.slug,
                "title": response.title,
                "topic": spec.topic,
                "product": spec.product,
                "concepts": spec.concepts,
                "level": spec.level,
                "path": str(path),
                "source_count": len(response.sources),
            }
        )
        print(f"[course] {spec.slug}: {len(response.sources)} sources -> {path}")

    (output_dir / "_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "_source_inventory.json").write_text(
        json.dumps([_document_payload(doc) for doc in documents], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[done] {len(index['courses'])} course scripts written to {output_dir}")


def _resolve_corpus_roots(overrides: list[str]) -> Iterable[Path]:
    if overrides:
        roots = [Path(item).expanduser().resolve() for item in overrides]
    else:
        project_root = Path(__file__).resolve().parents[3]
        roots = [
            project_root / "QUANTITATIVE_FINANCE",
            project_root / "Courses",
            project_root / "Papiers",
        ]
    for root in roots:
        if root.exists() and root.is_dir():
            yield root


def _ingest_roots(services, roots: Iterable[Path], *, force: bool) -> None:
    for root in roots:
        print(f"[ingest] {root}")
        results = services.ingestion.ingest_directory(
            root,
            metadata=DocumentMetadata(
                source=str(root),
                tags=["course_generation", "thepricinglibrary"],
            ),
            glob="*.pdf",
            recursive=True,
            force=force,
        )
        ingested = sum(1 for item in results if item.status == "ingested")
        skipped = sum(1 for item in results if item.status == "skipped")
        failed = sum(1 for item in results if item.status == "failed")
        chunks = sum(item.chunks_inserted for item in results)
        print(
            f"[ingest] done: ingested={ingested} skipped={skipped} "
            f"failed={failed} chunks={chunks}"
        )


def _course_markdown(spec: CourseSpec, response) -> str:
    concepts = ", ".join(spec.concepts)
    formula_block = _formula_bank_markdown(spec.slug)
    source_appendix = _source_appendix(response)
    return f"""---
slug: {spec.slug}
topic: {spec.topic}
product: {spec.product or ""}
level: {spec.level}
concepts: {concepts}
source_count: {len(response.sources)}
---

{response.content}

{formula_block}
{source_appendix}
"""


def _source_appendix(response) -> str:
    if "## Sources RAG a citer" in response.content:
        return ""
    source_lines = "\n".join(
        f"- [S{idx}] {src.title or src.source or src.document_id} "
        f"(chunk {src.chunk_index}, score {src.score:.3f})"
        for idx, src in enumerate(response.sources, start=1)
    )
    return f"\n## Source Appendix\n{source_lines or '- No retrieved source.'}\n"


def _formula_bank_markdown(slug: str) -> str:
    formulas = FORMULA_BANK.get(slug, [])
    if not formulas:
        return ""

    lines = [
        "## Formules de desk",
        "Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.",
    ]
    for idx, (title, formula, usage) in enumerate(formulas, start=1):
        lines.extend(
            [
                f"### F{idx} - {title}",
                "$$",
                formula,
                "$$",
                f"- Usage desk: {usage}",
            ]
        )
    return "\n".join(lines)


def _document_payload(doc) -> dict:
    return {
        "id": doc.id,
        "title": doc.title,
        "source": doc.source,
        "path": doc.path,
        "status": doc.status,
        "metadata": doc.metadata,
    }


def _now_label() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat(timespec="seconds")


if __name__ == "__main__":
    main()
