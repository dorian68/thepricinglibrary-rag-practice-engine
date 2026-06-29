"""Smoke test for the specialised multi-agent FIC trading floor (offline)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["TPL_LLM_PROVIDER"] = "template"

from pricinglibrary_rag.desk import DeskOrchestrator  # noqa: E402
from pricinglibrary_rag.desk_agents import DESKS, ROLE_CLASSES, get_floor  # noqa: E402
from pricinglibrary_rag.llm import TemplateLLM  # noqa: E402

FAILS: list[str] = []


def check(c, label, extra=""):
    print(f"  [{'ok ' if c else 'FAIL'}] {label}{(' - ' + extra) if extra and not c else ''}")
    if not c:
        FAILS.append(label)


print("=" * 64)
print("SPECIALISED FIC TRADING FLOOR SMOKE (offline)")
orch = DeskOrchestrator(TemplateLLM())

# 1. desks exist incl. Exotics; each desk has the full role roster with tools
check(set(["Rates", "Credit", "FX", "Exotics", "Commodities"]).issubset(DESKS.keys()), "desks: Rates/Credit/FX/Exotics/Commodities", str(list(DESKS)))
floor = get_floor()
roster = floor.roster()
for d, agents in roster.items():
    check(len(agents) == len(ROLE_CLASSES), f"{d} desk has {len(ROLE_CLASSES)} role agents", str(len(agents)))
    check(all(len(a["tools"]) >= 1 for a in agents), f"{d}: every agent owns >=1 tool")
    check(all(a["desk"] == d for a in agents), f"{d}: agents are specialised to the desk")

# 2. oil RFQ -> Commodities desk, WTI call priced 3.45 (matches the mockup)
r = orch.run("J'ai peur que le pétrole augmente dans 5 mois, que me proposez-vous ?")
check(r["desk"] == "Commodities", "oil routed to Commodities desk", r["desk"])
check(abs(r["pricing"]["est_price"] - 3.45) < 0.02, "WTI call priced 3.45", str(r["pricing"]["est_price"]))
check(abs(float(r["pricing"]["break_even"]) - 83.45) < 0.02, "break-even 83.45")
check(r["pricing"]["max_loss"] == 345, "max loss 345")
names = [a["name"] for a in r["agents"]]
check(names[0] == "Commodities Sales" and names[-1] == "Commodities Report", "chain Sales..Report on the desk", str(names))
check(all(a.get("tools") for a in r["agents"]), "every acting agent exposes its tools")
check(all(a.get("data") is not None for a in r["agents"]), "every agent produced a data object")

# 3. routing by product family
check(orch.run("Price a 5Y EUR callable note")["desk"] == "Rates", "callable note -> Rates desk")
check(orch.run("I think credit spreads will widen over 2 years")["desk"] == "Credit", "credit -> Credit desk")
check(orch.run("Hedge my EURUSD exposure")["desk"] == "FX", "fx -> FX desk")
check(orch.run("Build me an autocall on the index")["desk"] == "Exotics", "autocall -> Exotics desk")

# 4. exotics desk prices with MC model + exotic greeks (vega/correlation)
ex = orch.run("structured autocall note")
check(ex["desk"] == "Exotics", "structured -> Exotics")
check("Monte-Carlo" in ex["model_choice"]["model"], "exotics uses Monte-Carlo model", ex["model_choice"]["model"])
check("correlation" in ex["pricing_result"]["greeks"], "exotics computes correlation risk")

# 5. trader quote consistent bid<mid<ask; risk + audit present
for q, label in [(r, "commodities")]:
    qq = q["quote"]
    check(qq["bid"] < qq["mid"] < qq["ask"], f"{label}: bid<mid<ask", str(qq))
check(r["risk"]["dominant_risk"] != "" and r["risk"]["status"] in ("GREEN", "AMBER", "RED"), "risk computed")
check(len(r["audit_trail"]) >= 8, "audit trail covers the chain", str(len(r["audit_trail"])))

# 6. rates priced with DV01, credit with CS01
check(orch.run("Price a 5Y EUR swap")["pricing_result"].get("dv01", 0) > 0, "rates priced with DV01")
check(orch.run("buy 5y IG CDS protection")["pricing_result"].get("cs01", 0) > 0, "credit priced with CS01")

print("=" * 64)
if FAILS:
    print(f"FLOOR SMOKE: FAIL ({len(FAILS)})")
    for f in FAILS:
        print("  -", f)
    sys.exit(1)
print("FLOOR SMOKE: PASS")
