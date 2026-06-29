"""Seed REAL starter content into the platform DB (idempotent).

This is genuine, persisted, editable content (not mock theatre): blog posts are
real quant write-ups, jobs/threads are realistic starters. Blog is upserted by
slug; jobs/threads are only seeded when their table is empty, so re-running does
not duplicate.

    python scripts/seed_platform.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pricinglibrary_rag.config import Settings
from pricinglibrary_rag.platform_store import PlatformStore

store = PlatformStore(Settings.from_env().db_path)

BLOG = [
    dict(slug="delta-hedging-101", title="Delta hedging, the right way",
         author="The Pricing Library", read_minutes=6, tags=["greeks", "hedging"],
         excerpt="Why delta-neutral is only the first order, and what the gamma/theta trade-off really costs.",
         body=("# Delta hedging, the right way\n\n"
               "Delta-neutral removes the **first-order** spot exposure, but a hedged option book still "
               "lives or dies on the gamma/theta trade-off. On a small step $dt$ a delta-neutral long-gamma "
               "book earns approximately\n\n$$\\tfrac12\\,\\Gamma S^2\\,(\\sigma_{real}^2-\\sigma_{imp}^2)\\,dt,$$\n\n"
               "so you make money when realised vol beats the implied you paid, and you bleed theta otherwise. "
               "The practical lesson: re-hedge on a band, not a clock, and watch the gamma near expiry.")),
    dict(slug="put-call-parity", title="Put-call parity is your free arbitrage check",
         author="The Pricing Library", read_minutes=4, tags=["vanilla", "arbitrage"],
         excerpt="A model-independent identity that catches stale quotes before they cost you.",
         body=("# Put-call parity\n\n"
               "For European options, $C - P = S_0 e^{-qT} - K e^{-rT}$ holds with **no model assumption**. "
               "If a screen violates it beyond bid/offer, either the funding/dividend assumption is stale or "
               "one leg is mispriced. Quants use it as a sanity gate before trusting any surface.")),
    dict(slug="var-vs-es", title="VaR is not enough: meet Expected Shortfall",
         author="The Pricing Library", read_minutes=5, tags=["risk", "var"],
         excerpt="Why regulators moved to ES 97.5%, and what subadditivity has to do with it.",
         body=("# VaR vs Expected Shortfall\n\n"
               "VaR answers *how bad on a normal day* but says nothing about the tail beyond the quantile, and "
               "it is **not subadditive** in general. Expected Shortfall, $ES_\\alpha=\\mathbb{E}[L\\,|\\,L>VaR_\\alpha]$, "
               "averages the tail and is coherent — which is why FRTB moved capital to ES at 97.5%.")),
]

JOBS = [
    dict(title="Junior Quant Analyst", company="Helix Capital", location="Paris", kind="full-time",
         tags=["pricing", "python", "rates"], description="Build and validate pricing/risk for the rates desk. Strong stochastic calculus and Python."),
    dict(title="Quant Developer (Derivatives)", company="Northwind Markets", location="London", kind="full-time",
         tags=["c++", "monte-carlo", "exotics"], description="Own the exotic pricing library: Monte-Carlo, calibration, Greeks. C++ and numerics."),
    dict(title="Market Risk Intern", company="Aurora Bank", location="Remote", kind="internship",
         tags=["var", "stress", "python"], description="Support the VaR/ES and stress framework. Pandas, distributions, backtesting (Kupiec)."),
]

THREADS = [
    dict(channel="forum", title="How do you choose a re-hedge band?", author="quanta",
         body="Fixed time, fixed move, or Whalley-Wilmott style band around transaction costs? What do desks actually use?", tags=["hedging", "greeks"]),
    dict(channel="forum", title="Bootstrapping vs OIS discounting in practice", author="ratesguy",
         body="When does single-curve bootstrap break down enough that you must go multi-curve? Looking for a rule of thumb.", tags=["rates", "curve"]),
    dict(channel="projects", title="[Project] Open-source SABR calibrator", author="vol_carrier",
         body="Building a Hagan-2002 SABR fit with arbitrage checks. Looking for contributors and test smiles.", tags=["vol", "sabr"]),
]


def main() -> None:
    for p in BLOG:
        store.upsert_blog(slug=p["slug"], title=p["title"], author=p["author"], excerpt=p["excerpt"],
                          body=p["body"], tags=p["tags"], read_minutes=p["read_minutes"])
    print(f"blog: {len(store.list_blog())} posts")

    if not store.list_jobs():
        for j in JOBS:
            store.create_job(title=j["title"], company=j["company"], location=j["location"],
                             kind=j["kind"], tags=j["tags"], description=j["description"], posted_by="seed")
    print(f"jobs: {len(store.list_jobs())}")

    if not store.list_threads():
        for t in THREADS:
            store.create_thread(channel=t["channel"], title=t["title"], body=t["body"],
                                author=t["author"], tags=t["tags"])
    print(f"threads: {len(store.list_threads())}")
    print("counts:", store.counts())


if __name__ == "__main__":
    main()
