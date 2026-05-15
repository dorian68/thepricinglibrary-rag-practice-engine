from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .factory import build_services
from .schemas import (
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

    exercise = sub.add_parser("exercise", help="Generate a practical exercise.")
    exercise.add_argument("--topic")
    exercise.add_argument("--product")
    exercise.add_argument("--concept")
    exercise.add_argument("--prompt")
    exercise.add_argument("--difficulty", default="intermediate")
    exercise.add_argument("--format", default="mixed")
    exercise.add_argument("--questions", type=int, default=5)
    exercise.add_argument("--language", default="fr")

    course = sub.add_parser("course", help="Generate a course module.")
    course.add_argument("topic")
    course.add_argument("--product")
    course.add_argument("--concept", action="append", default=[])
    course.add_argument("--level", default="intermediate")
    course.add_argument("--duration", type=int, default=90)
    course.add_argument("--modules", type=int, default=4)
    course.add_argument("--language", default="fr")

    pack = sub.add_parser("material-pack", help="Generate a full pedagogical pack.")
    pack.add_argument("topic")
    pack.add_argument("--product")
    pack.add_argument("--concept", action="append", default=[])
    pack.add_argument("--level", default="intermediate")
    pack.add_argument("--duration", type=int, default=120)
    pack.add_argument("--exercises", type=int, default=3)
    pack.add_argument("--language", default="fr")

    serve = sub.add_parser("serve", help="Run the FastAPI server.")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)

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
