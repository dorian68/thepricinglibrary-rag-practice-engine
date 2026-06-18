"""Offline smoke test for the AG-UI streaming endpoint.

Runs the FastAPI app in-process with the template (no-cost) LLM provider and
asserts the AG-UI event contract: lifecycle order, RAG grounding tool call,
verified Black-Scholes parity, and frontend tool-control Custom events.

Usage (from Tools/pricinglibrary_rag_backend):
    TPL_LLM_PROVIDER=template python scripts/smoke_agui.py
"""

import json
import os
import sys

os.environ.setdefault("TPL_LLM_PROVIDER", "template")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402

from pricinglibrary_rag.api import create_app  # noqa: E402


def parse_sse(text: str) -> list[dict]:
    events = []
    for block in text.split("\n\n"):
        for line in block.splitlines():
            if line.startswith("data:"):
                raw = line[len("data:"):].strip()
                if raw and raw != "[DONE]":
                    events.append(json.loads(raw))
    return events


def post_run(client: TestClient, messages: list[dict], state: dict) -> list[dict]:
    payload = {
        "threadId": "thread_test",
        "runId": "run_test",
        "messages": messages,
        "state": state,
    }
    resp = client.post("/agent/ag-ui/run", json=payload)
    assert resp.status_code == 200, resp.text
    assert "text/event-stream" in resp.headers.get("content-type", ""), resp.headers
    return parse_sse(resp.text)


def types_of(events: list[dict]) -> list[str]:
    return [e.get("type") for e in events]


def main() -> int:
    app = create_app()
    client = TestClient(app)
    failures = []

    # 1) Default grounded conceptual answer.
    ev = post_run(
        client,
        [{"id": "m1", "role": "user", "content": "Explique-moi le delta d'une option"}],
        {"route": "/courses/greeks", "pageTitle": "Greeks", "concept": "delta", "lang": "fr"},
    )
    t = types_of(ev)
    if t[0] != "RunStarted":
        failures.append(f"first event is {t[0]}, expected RunStarted")
    if "RunFinished" not in t:
        failures.append("no RunFinished event")
    if "StateSnapshot" not in t:
        failures.append("no StateSnapshot event")
    if "TextMessageContent" not in t:
        failures.append("no TextMessageContent (no streamed text)")
    if "ToolCallResult" not in t:
        failures.append("no ToolCallResult (RAG grounding missing)")
    names = [e.get("toolCallName") for e in ev if e.get("type") == "ToolCallStart"]
    if "rag_search" not in names:
        failures.append(f"rag_search not called; tools={names}")

    # 2) Call-put parity on the BS pricer: must drive the tool + verify numbers.
    ev = post_run(
        client,
        [{"id": "m1", "role": "user", "content": "Montre-moi la parité call-put"}],
        {"route": "/tools/bs-pricer", "toolId": "bs-pricer",
         "toolParams": {"S": 100, "K": 100}, "lang": "fr"},
    )
    customs = [e for e in ev if e.get("type") == "Custom"]
    set_params = [e for e in customs if e.get("name") == "app.tool.set_params"]
    if not set_params:
        failures.append("call-put parity did not emit app.tool.set_params (tool not driven)")
    elif set_params[0]["value"]["tool"] != "bs-pricer":
        failures.append("set_params targeted the wrong tool")
    bs_calls = [e for e in ev if e.get("type") == "ToolCallStart" and e.get("toolCallName") == "compute_black_scholes"]
    if not bs_calls:
        failures.append("compute_black_scholes not called (no verified numbers)")
    # verify parity numbers inside the tool result
    parity_ok = False
    for e in ev:
        if e.get("type") == "ToolCallResult":
            try:
                payload = json.loads(e["content"])
            except Exception:
                continue
            if isinstance(payload, dict) and payload.get("parity_holds") is True:
                parity_ok = True
    if not parity_ok:
        failures.append("Black-Scholes parity_holds not True in any tool result")

    # 3) Exercise generation intent renders an exercise_block.
    ev = post_run(
        client,
        [{"id": "m1", "role": "user", "content": "Donne-moi un exercice"}],
        {"route": "/courses/black-scholes", "pageTitle": "Black-Scholes", "lang": "fr"},
    )
    renders = [e for e in ev if e.get("type") == "Custom" and e.get("name") == "app.render_component"]
    block_types = [r["value"]["component"] for r in renders]
    if "exercise_block" not in block_types:
        failures.append(f"no exercise_block rendered; blocks={block_types}")

    # 4) New quant UIBlocks via offline intents.
    for content, state, expected_block in [
        ("Comment évolue le vega quand la maturité augmente ?", {"route": "/tools/bs-pricer", "toolId": "bs-pricer"}, "greeks_sensitivity_block"),
        ("Fais une simulation monte carlo", {"route": "/courses/monte-carlo"}, "monte_carlo_simulation_block"),
        ("Montre le payoff d'un autocall avec barrière 60%", {"route": "/courses/exotics"}, "structured_product_payoff_block"),
    ]:
        ev = post_run(client, [{"id": "m1", "role": "user", "content": content}], {**state, "lang": "fr"})
        renders = [e for e in ev if e.get("type") == "Custom" and e.get("name") == "app.render_component"]
        blocks = [r["value"]["component"] for r in renders]
        if expected_block not in blocks:
            failures.append(f"'{content[:28]}...' did not render {expected_block}; got {blocks}")

    if failures:
        print("SMOKE AG-UI: FAIL")
        for f in failures:
            print("  -", f)
        return 1
    print("SMOKE AG-UI: PASS (lifecycle, RAG grounding, tool-drive + verified parity, exercise + greeks/MC/structured blocks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
