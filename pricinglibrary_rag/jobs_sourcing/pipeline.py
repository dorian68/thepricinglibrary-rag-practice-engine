"""Source -> finance-filter -> dedupe -> upsert pipeline."""
from __future__ import annotations

import time

from . import finance_filter as ff
from .providers import all_providers


def source_jobs(store, *, providers=None, limit_per: int = 70, threshold: int = 4,
                query: str = "finance", per_company: int = 10) -> dict:
    """Fetch from every available provider, keep finance-relevant postings, and
    upsert them into ``store`` (deduped by external_id). ``per_company`` caps the
    number of KEPT jobs per company so one big board doesn't crowd out the rest.
    Returns a report."""
    provs = providers if providers is not None else [p for p in all_providers() if p.available()]
    t0 = time.time()
    per_source: dict[str, dict] = {}
    seen_ids: set[str] = set()
    seen_tc: set[tuple] = set()  # (title, company) dedup — firms relist a role N times
    company_kept: dict[str, int] = {}
    inserted = skipped = filtered = 0
    for p in provs:
        rec = {"fetched": 0, "kept": 0, "inserted": 0, "error": None}
        try:
            postings = p.fetch(query=query, limit=limit_per)
        except Exception as exc:  # noqa: BLE001 - one provider must not kill the run
            rec["error"] = f"{type(exc).__name__}: {exc}"
            per_source[p.name] = rec
            continue
        rec["fetched"] = len(postings)
        for job in postings:
            if not job.title or not job.url or job.external_id in seen_ids:
                continue
            seen_ids.add(job.external_id)
            tc = (job.title.strip().lower(), (job.company or "").strip().lower())
            if tc in seen_tc:
                continue
            if not ff.is_relevant(job.title, job.description, job.tags, threshold=threshold):
                filtered += 1
                continue
            ckey = (job.company or "").strip().lower()
            if company_kept.get(ckey, 0) >= per_company:
                continue  # balance: cap kept jobs per company
            seen_tc.add(tc)
            company_kept[ckey] = company_kept.get(ckey, 0) + 1
            rec["kept"] += 1
            data = job.to_store()
            data["kind"] = data.get("kind") or ff.category(job.title, job.description)
            if not data["tags"]:
                data["tags"] = [ff.category(job.title, job.description)]
            status = store.upsert_job(**data)
            if status == "inserted":
                inserted += 1
                rec["inserted"] += 1
            else:
                skipped += 1
        per_source[p.name] = rec
    return {"providers_used": [p.name for p in provs], "inserted": inserted,
            "skipped_existing": skipped, "filtered_out": filtered,
            "elapsed_s": round(time.time() - t0, 2), "per_source": per_source,
            "totals_by_source": store.jobs_source_counts()}
