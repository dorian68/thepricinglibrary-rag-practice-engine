"""Jobs sourcing engine — multi-source finance job aggregation for the board.

Free/keyless providers (Remotive, Arbeitnow, Jobicy, The Muse, Greenhouse &
Lever company boards) populate the board on the free plan today; key-gated
providers (Apify/LinkedIn via APIFY_TOKEN, Adzuna) enrich it on paid plans.

    from pricinglibrary_rag.jobs_sourcing import source_jobs, provider_status
    report = source_jobs(platform_store)
"""
from __future__ import annotations

from .base import JobPosting, JobProvider
from .pipeline import source_jobs
from .providers import all_providers, provider_status

__all__ = ["source_jobs", "provider_status", "all_providers", "JobPosting", "JobProvider"]
