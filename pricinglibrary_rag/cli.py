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


def _parse_json_arg(parser: argparse.ArgumentParser, raw: str, name: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        parser.error(f"{name} must be valid JSON: {exc}")
    if not isinstance(data, dict):
        parser.error(f"{name} must be a JSON object")
    return data


def _parse_json_list_arg(parser: argparse.ArgumentParser, raw: str, name: str) -> list[dict[str, Any]]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        parser.error(f"{name} must be valid JSON: {exc}")
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        parser.error(f"{name} must be a JSON array of objects")
    return data


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

    tool_list = sub.add_parser("tool-list", help="List registered agent tools.")
    tool_list.add_argument("--agent-role")
    tool_list.add_argument("--desk")
    tool_list.add_argument("--permission")
    tool_desc = sub.add_parser("tool-describe", help="Describe one registered tool.")
    tool_desc.add_argument("tool_name")
    tool_run = sub.add_parser("tool-run", help="Run one registered tool with audited output.")
    tool_run.add_argument("tool_name")
    tool_run.add_argument("--payload", default="{}")
    sub.add_parser("tool-coverage", help="Show agent/tool coverage across both orchestrations.")

    session_create = sub.add_parser("session-create", help="Create an agent conversation session.")
    session_create.add_argument("--agent", required=True)
    session_create.add_argument("--channel", default="cli")
    session_create.add_argument("--external-user-id")
    session_create.add_argument("--title")
    session_create.add_argument("--route-json", default="{}")

    session_list = sub.add_parser("session-list", help="List conversation sessions.")
    session_list.add_argument("--agent")
    session_list.add_argument("--channel")
    session_list.add_argument("--status")
    session_list.add_argument("--limit", type=int, default=50)

    session_msg = sub.add_parser("session-add-message", help="Append a message to a session.")
    session_msg.add_argument("session_id")
    session_msg.add_argument("--role", required=True)
    session_msg.add_argument("--text", required=True)
    session_msg.add_argument("--visibility", default="agent_visible")
    session_msg.add_argument("--source", default="cli")
    session_msg.add_argument("--metadata", default="{}")

    session_history = sub.add_parser("session-history", help="Read sanitized session history.")
    session_history.add_argument("session_id")
    session_history.add_argument("--limit", type=int, default=20)
    session_history.add_argument("--offset", type=int, default=0)
    session_history.add_argument("--raw", action="store_true")

    session_artifacts = sub.add_parser("session-artifacts", help="List session artifacts.")
    session_artifacts.add_argument("session_id")

    session_run = sub.add_parser("session-run-tool", help="Run a ToolRegistry tool and attach result to a session.")
    session_run.add_argument("session_id")
    session_run.add_argument("tool_name")
    session_run.add_argument("--payload", default="{}")
    session_run.add_argument("--context", default="{}")
    session_run.add_argument("--agent")

    session_compact = sub.add_parser("session-compact", help="Create a deterministic compacted session summary.")
    session_compact.add_argument("session_id")
    session_compact.add_argument("--max-messages", type=int, default=20)
    session_compact.add_argument("--metadata", default="{}")

    session_summaries = sub.add_parser("session-summaries", help="List compacted summaries for a session.")
    session_summaries.add_argument("session_id")
    session_summaries.add_argument("--limit", type=int, default=20)

    session_fork = sub.add_parser("session-fork", help="Fork a session into another agent context.")
    session_fork.add_argument("session_id")
    session_fork.add_argument("--target-agent")
    session_fork.add_argument("--title")
    session_fork.add_argument("--include-last-messages", type=int, default=10)

    session_inject = sub.add_parser("session-inject", help="Inject messages/artifacts into a session.")
    session_inject.add_argument("session_id")
    session_inject.add_argument("--items", required=True)
    session_inject.add_argument("--source", default="cli:inject")

    session_rollback = sub.add_parser("session-rollback", help="Mark a non-destructive rollback point.")
    session_rollback.add_argument("session_id")
    session_rollback.add_argument("--message-id")
    session_rollback.add_argument("--keep-last", type=int)
    session_rollback.add_argument("--reason")

    session_events = sub.add_parser("session-events", help="List runtime events for a session.")
    session_events.add_argument("session_id")
    session_events.add_argument("--event-type")
    session_events.add_argument("--limit", type=int, default=100)

    turn_start = sub.add_parser("turn-start", help="Start a runtime turn in a session.")
    turn_start.add_argument("session_id")
    turn_start.add_argument("--objective", required=True)
    turn_start.add_argument("--input", default="{}")
    turn_start.add_argument("--parent-turn-id")
    turn_start.add_argument("--status", default="running")

    turn_complete = sub.add_parser("turn-complete", help="Complete or update a runtime turn.")
    turn_complete.add_argument("turn_id")
    turn_complete.add_argument("--output", default="{}")
    turn_complete.add_argument("--status", default="completed")

    turn_list = sub.add_parser("turn-list", help="List turns for a session.")
    turn_list.add_argument("session_id")
    turn_list.add_argument("--status")
    turn_list.add_argument("--limit", type=int, default=50)

    approval_request = sub.add_parser("approval-request", help="Request durable approval for a sensitive action.")
    approval_request.add_argument("session_id")
    approval_request.add_argument("--agent", required=True)
    approval_request.add_argument("--tool-name", required=True)
    approval_request.add_argument("--payload", default="{}")
    approval_request.add_argument("--reason", default="")
    approval_request.add_argument("--scope", default="once")
    approval_request.add_argument("--status", default="requested")

    approval_list = sub.add_parser("approval-list", help="List durable approval records.")
    approval_list.add_argument("--session-id")
    approval_list.add_argument("--status")
    approval_list.add_argument("--limit", type=int, default=50)

    approval_resolve = sub.add_parser("approval-resolve", help="Resolve a durable approval.")
    approval_resolve.add_argument("approval_id")
    approval_resolve.add_argument("--status", required=True, choices=["approved", "denied", "expired", "requested"])
    approval_resolve.add_argument("--decision-note")

    task_create = sub.add_parser("task-create", help="Create a detached agent task.")
    task_create.add_argument("--agent", required=True)
    task_create.add_argument("--title", required=True)
    task_create.add_argument("--type", default="subagent")
    task_create.add_argument("--parent-session-id")
    task_create.add_argument("--child-session-id")
    task_create.add_argument("--payload", default="{}")
    task_create.add_argument("--status", default="queued")

    task_list = sub.add_parser("task-list", help="List detached agent tasks.")
    task_list.add_argument("--status")
    task_list.add_argument("--agent")
    task_list.add_argument("--limit", type=int, default=50)

    task_update = sub.add_parser("task-update", help="Update a detached agent task.")
    task_update.add_argument("task_id")
    task_update.add_argument("--status")
    task_update.add_argument("--result-summary")
    task_update.add_argument("--child-session-id")

    mcp_tools = sub.add_parser("mcp-tools", help="Search/list MCP-exposed TPL tools.")
    mcp_tools.add_argument("--query")
    mcp_tools.add_argument("--agent-role")
    mcp_tools.add_argument("--permission")
    mcp_tools.add_argument("--limit", type=int, default=25)

    mcp_desc = sub.add_parser("mcp-describe", help="Describe one MCP-exposed tool.")
    mcp_desc.add_argument("tool_name")

    mcp_call = sub.add_parser("mcp-call", help="Call one MCP-exposed TPL tool.")
    mcp_call.add_argument("tool_name")
    mcp_call.add_argument("--payload", default="{}")
    mcp_call.add_argument("--context", default="{}")
    mcp_call.add_argument("--session-id")
    mcp_call.add_argument("--agent")

    mcp_handle = sub.add_parser("mcp-handle", help="Handle one JSON-RPC MCP-style request.")
    mcp_handle.add_argument("--request", required=True)

    sub.add_parser("mcp-serve", help="Serve the TPL MCP-style adapter over JSONL stdio.")

    gateway = sub.add_parser("gateway-inbound", help="Route one inbound channel message through the agent gateway.")
    gateway.add_argument("--channel", default="cli")
    gateway.add_argument("--external-user-id", required=True)
    gateway.add_argument("--body", required=True)
    gateway.add_argument("--target-agent", default="Chief of Staff")
    gateway.add_argument("--route-json", default="{}")
    gateway.add_argument("--tool-name")
    gateway.add_argument("--payload", default="{}")
    gateway.add_argument("--context", default="{}")

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

    if args.command in {"tool-list", "tool-describe", "tool-run", "tool-coverage"}:
        from .tool_registry import get_tool_registry

        registry = get_tool_registry()
        if args.command == "tool-list":
            _print_json(
                {
                    "tools": registry.list(
                        agent_role=args.agent_role,
                        desk=args.desk,
                        permission_scope=args.permission,
                    )
                }
            )
            return
        if args.command == "tool-describe":
            _print_json(registry.describe(args.tool_name))
            return
        if args.command == "tool-run":
            try:
                payload = json.loads(args.payload)
            except json.JSONDecodeError as exc:
                parser.error(f"--payload must be valid JSON: {exc}")
            result=registry.run(args.tool_name, payload=payload)
            _print_json(result)
            if not result.get("ok"):raise SystemExit(2)
            return
        if args.command == "tool-coverage":
            _print_json(registry.coverage_report())
            return

    if (
        args.command.startswith("session-")
        or args.command.startswith("task-")
        or args.command.startswith("turn-")
        or args.command.startswith("approval-")
    ):
        from .conversation_ledger import ConversationLedger

        ledger = ConversationLedger(services.store)
        if args.command == "session-create":
            _print_json(
                ledger.create_session(
                    agent_id=args.agent,
                    channel=args.channel,
                    external_user_id=args.external_user_id,
                    title=args.title,
                    route_metadata=_parse_json_arg(parser, args.route_json, "--route-json"),
                )
            )
            return
        if args.command == "session-list":
            _print_json(
                {
                    "sessions": ledger.list_sessions(
                        agent_id=args.agent,
                        channel=args.channel,
                        status=args.status,
                        limit=args.limit,
                    )
                }
            )
            return
        if args.command == "session-add-message":
            _print_json(
                ledger.add_message(
                    args.session_id,
                    role=args.role,
                    body=args.text,
                    visibility=args.visibility,
                    source=args.source,
                    metadata=_parse_json_arg(parser, args.metadata, "--metadata"),
                )
            )
            return
        if args.command == "session-history":
            _print_json(
                ledger.history(
                    args.session_id,
                    limit=args.limit,
                    offset=args.offset,
                    sanitized=not args.raw,
                )
            )
            return
        if args.command == "session-artifacts":
            _print_json({"artifacts": ledger.list_artifacts(args.session_id)})
            return
        if args.command == "session-run-tool":
            from .mcp_adapter import TplMcpAdapter

            adapter = TplMcpAdapter(store=services.store)
            result = adapter.call_tool(
                    args.tool_name,
                    payload=_parse_json_arg(parser, args.payload, "--payload"),
                    context=_parse_json_arg(parser, args.context, "--context"),
                    session_id=args.session_id,
                    agent_id=args.agent,
                )
            _print_json(result)
            if not result.get('tool_result',{}).get('ok'):raise SystemExit(2)
            return
        if args.command == "session-compact":
            _print_json(
                ledger.compact_session(
                    args.session_id,
                    max_messages=args.max_messages,
                    metadata=_parse_json_arg(parser, args.metadata, "--metadata"),
                )
            )
            return
        if args.command == "session-summaries":
            _print_json({"summaries": ledger.list_summaries(args.session_id, limit=args.limit)})
            return
        if args.command == "session-fork":
            _print_json(
                ledger.fork_session(
                    args.session_id,
                    target_agent=args.target_agent,
                    title=args.title,
                    include_last_messages=args.include_last_messages,
                )
            )
            return
        if args.command == "session-inject":
            _print_json(
                ledger.inject_items(
                    args.session_id,
                    _parse_json_list_arg(parser, args.items, "--items"),
                    source=args.source,
                )
            )
            return
        if args.command == "session-rollback":
            _print_json(
                ledger.rollback_session(
                    args.session_id,
                    message_id=args.message_id,
                    keep_last=args.keep_last,
                    reason=args.reason,
                )
            )
            return
        if args.command == "session-events":
            _print_json(
                {
                    "events": ledger.list_events(
                        session_id=args.session_id,
                        event_type=args.event_type,
                        limit=args.limit,
                    )
                }
            )
            return
        if args.command == "turn-start":
            _print_json(
                ledger.start_turn(
                    args.session_id,
                    objective=args.objective,
                    input_payload=_parse_json_arg(parser, args.input, "--input"),
                    parent_turn_id=args.parent_turn_id,
                    status=args.status,
                )
            )
            return
        if args.command == "turn-complete":
            _print_json(
                ledger.complete_turn(
                    args.turn_id,
                    output_payload=_parse_json_arg(parser, args.output, "--output"),
                    status=args.status,
                )
            )
            return
        if args.command == "turn-list":
            _print_json({"turns": ledger.list_turns(args.session_id, status=args.status, limit=args.limit)})
            return
        if args.command == "approval-request":
            _print_json(
                ledger.request_approval(
                    args.session_id,
                    agent_id=args.agent,
                    tool_name=args.tool_name,
                    payload=_parse_json_arg(parser, args.payload, "--payload"),
                    reason=args.reason,
                    scope=args.scope,
                    status=args.status,
                )
            )
            return
        if args.command == "approval-list":
            _print_json(
                {
                    "approvals": ledger.list_approvals(
                        session_id=args.session_id,
                        status=args.status,
                        limit=args.limit,
                    )
                }
            )
            return
        if args.command == "approval-resolve":
            _print_json(
                ledger.resolve_approval(
                    args.approval_id,
                    status=args.status,
                    decision_note=args.decision_note,
                )
            )
            return
        if args.command == "task-create":
            _print_json(
                ledger.create_task(
                    agent_id=args.agent,
                    title=args.title,
                    task_type=args.type,
                    parent_session_id=args.parent_session_id,
                    child_session_id=args.child_session_id,
                    payload=_parse_json_arg(parser, args.payload, "--payload"),
                    status=args.status,
                )
            )
            return
        if args.command == "task-list":
            _print_json(
                {
                    "tasks": ledger.list_tasks(
                        status=args.status,
                        agent_id=args.agent,
                        limit=args.limit,
                    )
                }
            )
            return
        if args.command == "task-update":
            _print_json(
                ledger.update_task(
                    args.task_id,
                    status=args.status,
                    result_summary=args.result_summary,
                    child_session_id=args.child_session_id,
                )
            )
            return

    if args.command.startswith("mcp-"):
        from .mcp_adapter import TplMcpAdapter

        adapter = TplMcpAdapter(store=services.store)
        if args.command == "mcp-tools":
            _print_json(
                adapter.tool_search(
                    query=args.query,
                    agent_role=args.agent_role,
                    permission=args.permission,
                    limit=args.limit,
                )
            )
            return
        if args.command == "mcp-describe":
            _print_json(adapter.describe_tool(args.tool_name))
            return
        if args.command == "mcp-call":
            result=adapter.call_tool(
                    args.tool_name,
                    payload=_parse_json_arg(parser, args.payload, "--payload"),
                    context=_parse_json_arg(parser, args.context, "--context"),
                    session_id=args.session_id,
                    agent_id=args.agent,
                )
            _print_json(result)
            if not result["tool_result"].get("ok"):raise SystemExit(2)
            return
        if args.command == "mcp-handle":
            request = _parse_json_arg(parser, args.request, "--request")
            _print_json(adapter.jsonrpc(request))
            return
        if args.command == "mcp-serve":
            adapter.serve_stdio()
            return

    if args.command == "gateway-inbound":
        from .agent_gateway import AgentInteractionGateway

        gateway = AgentInteractionGateway(services.store)
        _print_json(
            gateway.handle_inbound(
                channel=args.channel,
                external_user_id=args.external_user_id,
                body=args.body,
                target_agent=args.target_agent,
                route_metadata=_parse_json_arg(parser, args.route_json, "--route-json"),
                tool_name=args.tool_name,
                payload=_parse_json_arg(parser, args.payload, "--payload"),
                context=_parse_json_arg(parser, args.context, "--context"),
            )
        )
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
