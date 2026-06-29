"""Smoke test for the absorbed side-projects: market-data layer, VolSurface
crypto-vol desk, and the TRADING Strategy Lab — end to end incl. HTTP routes.

Run:  python scripts/smoke_integrations.py
Exit code 0 = all checks passed.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CHECKS: list[tuple[str, bool, str]] = []


def check(name, cond, detail=""):
    CHECKS.append((name, bool(cond), str(detail)))


def main():
    # 1) market-data layer -------------------------------------------------
    from pricinglibrary_rag import marketdata as md
    provs = {p["name"]: p for p in md.provider_status()}
    check("marketdata: yfinance+fred keyless", provs["yfinance"]["available"] and provs["fred"]["available"])
    btc = md.get_history("BTC-USD")
    check("marketdata: BTC history cached", len(btc) > 1000, f"{len(btc)} rows")
    spx = md.get_history("^GSPC")
    check("marketdata: SPX history cached", len(spx) > 5000, f"{len(spx)} rows")

    # 2) VolSurface bridge -------------------------------------------------
    from pricinglibrary_rag import volsurface_bridge as vb
    check("volsurface: engine wired", vb.engine_name() in ("volsurface", "local-bs"), vb.engine_name())
    o = vb.price_option(100, 100, 1.0, 0.04, 0.5, "call")
    check("volsurface: BS price sane", 20 < o["price"] < 23 and o["delta"] > 0, o["price"])
    rv = vb.realized_vol("BTC")
    check("volsurface: realized vol from history", rv.get("rv_30d") is not None, rv.get("rv_30d"))
    rm = vb.risk_matrix(60000, 60000, 0.1, 0.04, 0.6)
    check("volsurface: 7x5 risk matrix", len(rm["grid"]) == 5 and len(rm["grid"][0]) == 7)

    # 3) Crypto Vol desk through the orchestrator --------------------------
    from pricinglibrary_rag.factory import build_services
    from pricinglibrary_rag.desk import DeskOrchestrator
    desk = DeskOrchestrator(build_services().llm)
    r = desk.run("Price me an ATM Bitcoin call option for 3 months")
    check("cryptovol desk: routed", r["desk"] == "CryptoVol", r["desk"])
    check("cryptovol desk: real engine priced", (r["pricing_result"] or {}).get("engine") == vb.engine_name())
    check("cryptovol desk: 8 agents", len(r["agents"]) == 8, len(r["agents"]))
    check("cryptovol desk: greeks present", "vega" in (r["pricing_result"] or {}).get("greeks", {}))

    # 4) stateful room: crypto wired --------------------------------------
    from pricinglibrary_rag.desk_state import get_room
    snap = get_room().snapshot()
    check("room: BTC/ETH in market watch", "BTC" in snap["market_watch"] and "ETH" in snap["market_watch"])
    check("room: CryptoVol book seeded", len(snap["books"].get("CryptoVol", [])) >= 2)

    # 5) Strategy Lab (subprocess into TRADING) ---------------------------
    from pricinglibrary_rag import strategylab as lab
    check("strategylab: engine available", lab.available())
    bt = lab.backtest("EURUSD", max_bars=20000)
    check("strategylab: EURUSD backtest ran", "metrics" in bt and not bt.get("error"), bt.get("error"))
    check("strategylab: produced trades+equity", bt.get("n_trades", 0) >= 1 and len(bt.get("equity", [])) > 10,
          f"trades={bt.get('n_trades')} eq={len(bt.get('equity', []))}")

    # 6) HTTP routes via TestClient ---------------------------------------
    from fastapi.testclient import TestClient
    from pricinglibrary_rag.api import create_app
    client = TestClient(create_app())
    check("http: /market/providers", client.get("/market/providers").status_code == 200)
    h = client.get("/market/history/BTC-USD?points=50")
    check("http: /market/history", h.status_code == 200 and h.json().get("rows", 0) > 1000)
    cv = client.get("/agent/crypto/vol?asset=BTC")
    check("http: /agent/crypto/vol", cv.status_code == 200 and cv.json().get("engine"))
    si = client.get("/strategy/instruments")
    check("http: /strategy/instruments", si.status_code == 200 and len(si.json().get("instruments", [])) >= 4)
    dr = client.post("/agent/desk/run", json={"query": "bullish bitcoin 3 months option"})
    check("http: /agent/desk/run -> CryptoVol", dr.status_code == 200 and dr.json().get("desk") == "CryptoVol")

    # report ---------------------------------------------------------------
    passed = sum(1 for _, ok, _ in CHECKS if ok)
    print(f"\n=== SMOKE: integrations (side-projects absorbed) ===")
    for name, ok, detail in CHECKS:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if detail and not ok else (f"  -> {detail}" if detail else "")))
    print(f"\n{passed}/{len(CHECKS)} checks passed")
    return 0 if passed == len(CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())
