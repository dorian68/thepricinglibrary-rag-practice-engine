"""Smoke test for the stateful FIC trading room (time passes, books are live)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pricinglibrary_rag.desk_state import TradingRoom  # noqa: E402

FAILS: list[str] = []


def check(c, label, extra=""):
    print(f"  [{'ok ' if c else 'FAIL'}] {label}{(' - ' + extra) if extra and not c else ''}")
    if not c:
        FAILS.append(label)


print("=" * 64)
print("STATEFUL FIC TRADING ROOM SMOKE")
room = TradingRoom(seed=42)
s0 = room.snapshot()

# 1. seeded live books exist across desks
check(s0["desk"]["positions"] >= 6, "starter book has >=6 live positions", str(s0["desk"]["positions"]))
check(len(s0["books"]["Rates"]) >= 1, "Rates book populated")
check(len(s0["books"]["Credit"]) >= 1, "Credit book populated")
check(abs(s0["desk"]["dv01"]) > 0, "aggregate DV01 non-zero", str(s0["desk"]["dv01"]))
check(abs(s0["desk"]["cs01"]) > 0, "aggregate CS01 non-zero", str(s0["desk"]["cs01"]))

# 2. time passes: clock + market + maturities move on tick
spx0, eur0 = s0["spx"], s0["market_watch"]["EUR/USD"]["v"]
clock0 = s0["clock"]
room.tick(3600)  # advance one hour
s1 = room.snapshot()
check(s1["clock"] != clock0, "clock advanced", f"{clock0} -> {s1['clock']}")
check(s1["spx"] != spx0, "SPX moved with the market", f"{spx0} -> {s1['spx']}")
check(s1["market_watch"]["EUR/USD"]["v"] != eur0, "EUR/USD moved")

# 3. P&L is live: marking to market changes book P&L after a move
room.reset_session_pnl()
p_before = room.total_pnl()
for _ in range(20):
    room.tick(600)
p_after = room.total_pnl()
check(p_before == 0.0, "session P&L reset to 0")
check(p_after != 0.0, "P&L moved as the market evolved", str(p_after))
check(len(room.snapshot()["desk"]["pnl_curve"]) > 1, "P&L curve is accumulating")

# 4. positions revalue (MtM differs from 0 for moved book)
moved = any(abs(p["mtm"]) > 0 for b in room.snapshot()["books"].values() for p in b)
check(moved, "positions are marked to market (non-zero MtM)")

# 5. trading from an RFQ adds a live position to a book
n_before = room.positions_count()
room.add_swap("EUR", 50_000_000, +1, 5.0, label="RFQ payer")
room.revalue()
check(room.positions_count() == n_before + 1, "RFQ trade booked a new position")

# 6. risk status + limit usage computed
check(room.risk_status() in ("GREEN", "AMBER", "RED"), "risk status computed", room.risk_status())
check(0 <= room.snapshot()["desk"]["limit_usage"] <= 5, "limit usage computed")

# 7. determinism: same seed -> same first move
r2 = TradingRoom(seed=42)
r2.tick(3600)
check(abs(r2.snapshot()["spx"] - s1["spx"]) < 1e-6, "seeded run is reproducible", f"{r2.snapshot()['spx']} vs {s1['spx']}")

print("=" * 64)
if FAILS:
    print(f"STATE SMOKE: FAIL ({len(FAILS)})")
    for f in FAILS:
        print("  -", f)
    sys.exit(1)
print("STATE SMOKE: PASS")
