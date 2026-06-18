from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .factory import build_services
from .schemas import (
    CalculationRequest,
    CourseRequest,
    DocumentMetadata,
    ExerciseRequest,
    IngestRequest,
    MaterialPackRequest,
    SearchRequest,
)


def _print_json(data: Any) -> None:
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pricinglibrary-rag",
        description="Local RAG backend tools for ThePricingLibrary.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db", help="Create or migrate the local SQLite database.")

    ingest = sub.add_parser("ingest", help="Ingest one file or a directory.")
    ingest.add_argument("path")
    ingest.add_argument("--recursive", action="store_true")
    ingest.add_argument("--glob", default="*.pdf")
    ingest.add_argument("--force", action="store_true")
    ingest.add_argument("--title")
    ingest.add_argument("--source")
    ingest.add_argument("--asset-class")
    ingest.add_argument("--product")
    ingest.add_argument("--concept", action="append", default=[])
    ingest.add_argument("--tag", action="append", default=[])

    search = sub.add_parser("search", help="Search the local RAG corpus.")
    search.add_argument("query")
    search.add_argument("--top-k", type=int, default=8)
    search.add_argument("--product")
    search.add_argument("--concept")
    search.add_argument("--asset-class")

    calc = sub.add_parser("calculate", help="Run deterministic practice calculators.")
    calc.add_argument("prompt")
    calc.add_argument("--family", default="auto")

    exercise = sub.add_parser("exercise", help="Generate a practical exercise.")
    exercise.add_argument("--topic")
    exercise.add_argument("--product")
    exercise.add_argument("--concept")
    exercise.add_argument("--prompt")
    exercise.add_argument("--difficulty", default="intermediate")
    exercise.add_argument("--format", default="mixed")
    exercise.add_argument("--questions", type=int, default=5)
    exercise.add_argument("--language", default="fr")

    agent_exercise = sub.add_parser(
        "agent-exercise",
        help="Generate a desk-first exercise through the Practice Agent.",
    )
    agent_exercise.add_argument("--topic")
    agent_exercise.add_argument("--product")
    agent_exercise.add_argument("--concept")
    agent_exercise.add_argument("--prompt")
    agent_exercise.add_argument("--difficulty", default="intermediate")
    agent_exercise.add_argument("--format", default="risk_management")
    agent_exercise.add_argument("--questions", type=int, default=5)
    agent_exercise.add_argument("--language", default="fr")

    course = sub.add_parser("course", help="Generate a course module.")
    course.add_argument("topic")
    course.add_argument("--product")
    course.add_argument("--concept", action="append", default=[])
    course.add_argument("--level", default="intermediate")
    course.add_argument("--duration", type=int, default=90)
    course.add_argument("--modules", type=int, default=4)
    course.add_argument("--language", default="fr")

    agent_course = sub.add_parser(
        "agent-course",
        help="Generate a practice-first course through the Practice Agent.",
    )
    agent_course.add_argument("topic")
    agent_course.add_argument("--product")
    agent_course.add_argument("--concept", action="append", default=[])
    agent_course.add_argument("--level", default="intermediate")
    agent_course.add_argument("--duration", type=int, default=90)
    agent_course.add_argument("--modules", type=int, default=4)
    agent_course.add_argument("--language", default="fr")

    pack = sub.add_parser("material-pack", help="Generate a full pedagogical pack.")
    pack.add_argument("topic")
    pack.add_argument("--product")
    pack.add_argument("--concept", action="append", default=[])
    pack.add_argument("--level", default="intermediate")
    pack.add_argument("--duration", type=int, default=120)
    pack.add_argument("--exercises", type=int, default=3)
    pack.add_argument("--language", default="fr")

    library = sub.add_parser("library", help="List generated course/exercise assets.")
    library.add_argument("--kind")
    library.add_argument("--limit", type=int, default=20)

    evaluate = sub.add_parser("evaluate", help="Run product quality evaluation cases.")
    evaluate.add_argument("--limit", type=int)

    sub.add_parser(
        "pedagogy-stats",
        help="Show pedagogical coverage of the ingested corpus.",
    )

    backfill = sub.add_parser(
        "backfill-pedagogy",
        help="Classify and score chunks ingested before pedagogical metadata.",
    )
    backfill.add_argument("--limit", type=int, default=None)
    backfill.add_argument("--batch-size", type=int, default=500)
    backfill.add_argument(
        "--force",
        action="store_true",
        help="Re-classify all chunks, not only those missing pedagogy.",
    )

    enrich = sub.add_parser(
        "enrich-documents",
        help="Infer theme/subtheme/asset_class for already-ingested documents.",
    )
    enrich.add_argument("--force", action="store_true", help="Overwrite existing theme.")

    serve = sub.add_parser("serve", help="Run the FastAPI server.")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)

    sub.add_parser("billing-config", help="Show Stripe billing configuration (no secrets).")
    bco = sub.add_parser("billing-checkout", help="Create a checkout session (mock if Stripe unset).")
    bco.add_argument("--plan", default="starter", choices=["starter", "student", "pro"])
    bco.add_argument("--email", default=None)
    bent = sub.add_parser("billing-entitlement", help="Show a user's entitlement.")
    bent.add_argument("email")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    services = build_services()

    if args.command == "init-db":
        _print_json(
            {
                "status": "ok",
                "db_path": str(services.settings.db_path),
                "embedding_backend": services.embeddings.name,
                "llm": services.llm.name,
            }
        )
        return

    if args.command == "ingest":
        metadata = DocumentMetadata(
            title=args.title,
            source=args.source,
            asset_class=args.asset_class,
            product=args.product,
            concepts=args.concept,
            tags=args.tag,
        )
        request = IngestRequest(
            path=args.path,
            metadata=metadata,
            recursive=args.recursive or Path(args.path).is_dir(),
            glob=args.glob,
            force=args.force,
        )
        if request.recursive:
            root = Path(request.path).expanduser().resolve()
            files = sorted(root.rglob(request.glob))
            result = []
            for idx, file_path in enumerate(files, start=1):
                item = services.ingestion.ingest_file(
                    file_path,
                    metadata=request.metadata,
                    force=request.force,
                )
                result.append(item)
                print(
                    json.dumps(
                        {
                            "index": idx,
                            "total": len(files),
                            "file": str(file_path),
                            **item.model_dump(),
                        },
                        ensure_ascii=False,
                        default=str,
                    ),
                    flush=True,
                )
            print(
                json.dumps(
                    {
                        "summary": {
                            "total": len(result),
                            "ingested": sum(1 for item in result if item.status == "ingested"),
                            "skipped": sum(1 for item in result if item.status == "skipped"),
                            "failed": sum(1 for item in result if item.status == "failed"),
                            "chunks": sum(item.chunks_inserted for item in result),
                        }
                    },
                    ensure_ascii=False,
                    default=str,
                ),
                flush=True,
            )
            return
        else:
            result = [
                services.ingestion.ingest_file(
                    request.path,
                    metadata=request.metadata,
                    force=request.force,
                )
            ]
        _print_json([item.model_dump() for item in result])
        return

    if args.command == "search":
        result = services.retriever.search(
            SearchRequest(
                query=args.query,
                top_k=args.top_k,
                product=args.product,
                concept=args.concept,
                asset_class=args.asset_class,
            )
        )
        _print_json(result)
        return

    if args.command == "calculate":
        request = CalculationRequest(prompt=args.prompt, family_hint=args.family)
        pack = services.generator.calculator.build_pack(
            request.prompt,
            family_hint=request.family_hint,
        )
        print(pack.as_markdown())
        return

    if args.command == "library":
        items = services.store.list_generation_runs(kind=args.kind, limit=args.limit)
        _print_json(
            [
                {
                    "id": item.id,
                    "kind": item.kind,
                    "title": item.title,
                    "created_at": item.created_at,
                }
                for item in items
            ]
        )
        return

    if args.command == "evaluate":
        report = services.evaluator.run_generation_suite(
            services.generator,
            limit=args.limit,
        )
        _print_json(report)
        return

    if args.command == "exercise":
        result = services.generator.generate_exercise(
            ExerciseRequest(
                topic=args.topic,
                product=args.product,
                concept=args.concept,
                free_prompt=args.prompt,
                difficulty=args.difficulty,
                exercise_format=args.format,
                number_of_questions=args.questions,
                language=args.language,
            )
        )
        print(result.content)
        return

    if args.command == "agent-exercise":
        from .practice_agent import PracticeAgent

        result = PracticeAgent(services.generator).create_exercise(
            ExerciseRequest(
                topic=args.topic,
                product=args.product,
                concept=args.concept,
                free_prompt=args.prompt,
                difficulty=args.difficulty,
                exercise_format=args.format,
                number_of_questions=args.questions,
                language=args.language,
            )
        )
        print(result.content)
        return

    if args.command == "course":
        result = services.generator.generate_course(
            CourseRequest(
                topic=args.topic,
                product=args.product,
                concepts=args.concept,
                level=args.level,
                duration_minutes=args.duration,
                module_count=args.modules,
                language=args.language,
            )
        )
        print(result.content)
        return

    if args.command == "agent-course":
        from .practice_agent import PracticeAgent

        result = PracticeAgent(services.generator).create_course(
            CourseRequest(
                topic=args.topic,
                product=args.product,
                concepts=args.concept,
                level=args.level,
                duration_minutes=args.duration,
                module_count=args.modules,
                language=args.language,
            )
        )
        print(result.content)
        return

    if args.command == "material-pack":
        result = services.generator.generate_material_pack(
            MaterialPackRequest(
                topic=args.topic,
                product=args.product,
                concepts=args.concept,
                level=args.level,
                duration_minutes=args.duration,
                exercise_count=args.exercises,
                language=args.language,
            )
        )
        print(result.content)
        return

    if args.command == "pedagogy-stats":
        _print_json(services.store.pedagogy_stats())
        return

    if args.command == "backfill-pedagogy":
        from .pedagogy import classify_chunk

        updated = services.store.backfill_pedagogy(
            lambda content, section_title: classify_chunk(content, section_title=section_title),
            batch_size=args.batch_size,
            limit=args.limit,
            force=args.force,
        )
        services.retriever.refresh()
        _print_json({"status": "ok", "chunks_updated": updated, **services.store.pedagogy_stats()})
        return

    if args.command == "enrich-documents":
        from .pedagogy import infer_document_theme

        documents = services.store.list_documents(limit=100000)
        updated = 0
        theme_counts: dict[str, int] = {}
        for doc in documents:
            metadata = dict(doc.metadata or {})
            extra = dict(metadata.get("extra") or {})
            if extra.get("theme") and not args.force:
                theme_counts[extra["theme"]] = theme_counts.get(extra["theme"], 0) + 1
                continue
            sample = services.store.document_text_sample(doc.id)
            theme = infer_document_theme(sample, doc.title)
            extra["theme"] = theme["theme"]
            extra["subtheme"] = theme["subtheme"]
            extra["theme_confidence"] = theme["theme_confidence"]
            metadata["extra"] = extra
            if not metadata.get("asset_class") or metadata.get("asset_class") == "multi_asset":
                metadata["asset_class"] = theme["asset_class"]
            services.store.update_document_metadata(doc.id, metadata)
            theme_counts[theme["theme"]] = theme_counts.get(theme["theme"], 0) + 1
            updated += 1
        services.retriever.refresh()
        _print_json(
            {
                "status": "ok",
                "documents": len(documents),
                "updated": updated,
                "theme_distribution": dict(sorted(theme_counts.items(), key=lambda kv: kv[1], reverse=True)),
            }
        )
        return

    if args.command == "billing-config":
        _print_json(services.billing.config_summary())
        return

    if args.command == "billing-checkout":
        from .billing import BillingError

        try:
            session = services.billing.create_checkout_session(args.plan, email=args.email)
        except BillingError as exc:
            parser.error(str(exc))
        _print_json(
            {"id": session.id, "url": session.url, "plan": session.plan, "mode": session.mode}
        )
        return

    if args.command == "billing-entitlement":
        _print_json(services.billing.entitlement(args.email))
        return

    if args.command == "serve":
        import uvicorn

        uvicorn.run(
            "pricinglibrary_rag.api:app",
            host=args.host,
            port=args.port,
            reload=False,
        )
        return

    parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
