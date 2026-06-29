"""Job providers. Free/keyless ones populate the board today; key-gated ones
(Apify LinkedIn, Adzuna) activate when their env keys are set.
"""
from __future__ import annotations

import re

from .base import JobPosting, JobProvider, http_json, make_id

_TAG_HTML = re.compile(r"<[^>]+>")


def _strip_html(s: str | None, limit: int = 600) -> str | None:
    if not s:
        return None
    txt = _TAG_HTML.sub(" ", s)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt[:limit] or None


# --- FREE / KEYLESS ---------------------------------------------------------
class RemotiveProvider(JobProvider):
    name = "remotive"

    def fetch(self, *, query="finance", limit=50):
        d = http_json(f"https://remotive.com/api/remote-jobs?search={query}&limit={limit}")
        out = []
        for j in d.get("jobs", []):
            out.append(JobPosting(
                external_id=make_id("remotive", str(j.get("id")), j.get("title", "")),
                title=j.get("title", ""), company=j.get("company_name", ""),
                url=j.get("url", ""), source="remotive", location=j.get("candidate_required_location"),
                description=_strip_html(j.get("description")), tags=j.get("tags", []) or [],
                remote=True, kind=j.get("job_type")))
        return out


class ArbeitnowProvider(JobProvider):
    name = "arbeitnow"

    def fetch(self, *, query="finance", limit=100):
        d = http_json("https://www.arbeitnow.com/api/job-board-api")
        out = []
        for j in d.get("data", [])[:limit]:
            out.append(JobPosting(
                external_id=make_id("arbeitnow", j.get("slug", ""), j.get("title", "")),
                title=j.get("title", ""), company=j.get("company_name", ""),
                url=j.get("url", ""), source="arbeitnow", location=j.get("location"),
                description=_strip_html(j.get("description")), tags=j.get("tags", []) or [],
                remote=bool(j.get("remote")), kind=(j.get("job_types") or [None])[0]))
        return out


class JobicyProvider(JobProvider):
    name = "jobicy"

    def fetch(self, *, query="finance", limit=50):
        d = http_json(f"https://jobicy.com/api/v2/remote-jobs?count={min(limit,50)}&tag={query}")
        out = []
        for j in d.get("jobs", []):
            out.append(JobPosting(
                external_id=make_id("jobicy", str(j.get("id")), j.get("jobTitle", "")),
                title=j.get("jobTitle", ""), company=j.get("companyName", ""),
                url=j.get("url", ""), source="jobicy", location=j.get("jobGeo"),
                description=_strip_html(j.get("jobExcerpt")), tags=j.get("jobIndustry", []) or [],
                remote=True, kind=(j.get("jobType") or [None])[0] if isinstance(j.get("jobType"), list) else j.get("jobType")))
        return out


class TheMuseProvider(JobProvider):
    name = "themuse"

    def fetch(self, *, query="finance", limit=40):
        out = []
        for page in (1, 2):
            try:
                d = http_json(f"https://www.themuse.com/api/public/jobs?category=Finance&page={page}")
            except Exception:
                break
            for j in d.get("results", []):
                locs = ", ".join(l.get("name", "") for l in (j.get("locations") or [])) or None
                out.append(JobPosting(
                    external_id=make_id("themuse", str(j.get("id")), j.get("name", "")),
                    title=j.get("name", ""), company=(j.get("company") or {}).get("name", ""),
                    url=(j.get("refs") or {}).get("landing_page", ""), source="themuse",
                    location=locs, description=_strip_html(j.get("contents")),
                    tags=[c.get("name") for c in (j.get("categories") or [])], kind=j.get("type")))
            if len(out) >= limit:
                break
        return out[:limit]


# Verified quant/market-finance firms publishing on public Greenhouse boards.
_GREENHOUSE = ["point72", "janestreet", "imc", "squarepointcapital", "jumptrading",
               "aqr", "virtu", "flowtraders", "akunacapital", "oldmissioncapital",
               "marshallwace", "optiver"]
_GH_NAMES = {"point72": "Point72", "janestreet": "Jane Street", "imc": "IMC Trading",
             "squarepointcapital": "Squarepoint Capital", "jumptrading": "Jump Trading",
             "aqr": "AQR Capital", "virtu": "Virtu Financial", "flowtraders": "Flow Traders",
             "akunacapital": "Akuna Capital", "oldmissioncapital": "Old Mission",
             "marshallwace": "Marshall Wace", "optiver": "Optiver"}
_LEVER = ["voleon", "quantco", "kpler", "tower-research-capital"]


class GreenhouseProvider(JobProvider):
    name = "greenhouse"

    def fetch(self, *, query="finance", limit=300):
        # Offer plenty of raw jobs per firm; the pipeline caps KEPT (relevant)
        # jobs per company, so balancing happens after the finance filter.
        per_company = 70
        out = []
        for slug in _GREENHOUSE:
            try:
                d = http_json(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true")
            except Exception:
                continue
            company = _GH_NAMES.get(slug, slug.title())
            taken = 0
            for j in d.get("jobs", []):
                if taken >= per_company:
                    break
                out.append(JobPosting(
                    external_id=make_id("greenhouse", slug, str(j.get("id"))),
                    title=j.get("title", ""), company=company,
                    url=j.get("absolute_url", ""), source="greenhouse",
                    location=(j.get("location") or {}).get("name"),
                    description=_strip_html(j.get("content")),
                    tags=[str(d2.get("value")) for d2 in (j.get("metadata") or [])
                          if d2.get("value") and isinstance(d2.get("value"), str)][:4]))
                taken += 1
        return out


class LeverProvider(JobProvider):
    name = "lever"

    def fetch(self, *, query="finance", limit=100):
        out = []
        for slug in _LEVER:
            try:
                rows = http_json(f"https://api.lever.co/v0/postings/{slug}?mode=json")
            except Exception:
                continue
            for j in rows if isinstance(rows, list) else []:
                cats = j.get("categories") or {}
                out.append(JobPosting(
                    external_id=make_id("lever", slug, j.get("id", "")),
                    title=j.get("text", ""), company=slug.replace("-", " ").title(),
                    url=j.get("hostedUrl", ""), source="lever",
                    location=cats.get("location"), description=_strip_html(j.get("descriptionPlain")),
                    tags=[cats.get("team"), cats.get("department")], kind=cats.get("commitment")))
                if len(out) >= limit:
                    return out
        return out


# --- KEY-GATED (paid enrichment) --------------------------------------------
class AdzunaProvider(JobProvider):
    name = "adzuna"
    requires_key = True
    env_key = "ADZUNA_APP_ID"  # also needs ADZUNA_APP_KEY

    def available(self):
        import os
        return bool(os.environ.get("ADZUNA_APP_ID") and os.environ.get("ADZUNA_APP_KEY"))

    def fetch(self, *, query="quantitative finance", limit=50):
        import os
        aid, akey = os.environ["ADZUNA_APP_ID"], os.environ["ADZUNA_APP_KEY"]
        country = os.environ.get("ADZUNA_COUNTRY", "gb")
        url = (f"https://api.adzuna.com/v1/api/jobs/{country}/search/1?app_id={aid}&app_key={akey}"
               f"&what={query.replace(' ', '%20')}&results_per_page={min(limit,50)}&content-type=application/json")
        d = http_json(url)
        out = []
        for j in d.get("results", []):
            out.append(JobPosting(
                external_id=make_id("adzuna", str(j.get("id")), j.get("title", "")),
                title=j.get("title", ""), company=(j.get("company") or {}).get("display_name", ""),
                url=j.get("redirect_url", ""), source="adzuna",
                location=(j.get("location") or {}).get("display_name"),
                description=_strip_html(j.get("description")), kind=j.get("contract_time")))
        return out


class ApifyLinkedInProvider(JobProvider):
    """LinkedIn Jobs via an Apify actor. Gated by APIFY_TOKEN; actor configurable."""
    name = "apify_linkedin"
    requires_key = True
    env_key = "APIFY_TOKEN"

    def fetch(self, *, query="quantitative finance", limit=50):
        import os
        token = os.environ["APIFY_TOKEN"]
        actor = os.environ.get("APIFY_LINKEDIN_ACTOR", "bebity~linkedin-jobs-scraper")
        url = f"https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items?token={token}"
        payload = {"title": query, "location": os.environ.get("APIFY_LINKEDIN_LOCATION", ""),
                   "rows": min(limit, 100), "proxy": {"useApifyProxy": True}}
        rows = http_json(url, method="POST", body=payload, timeout=180)
        out = []
        for j in rows if isinstance(rows, list) else []:
            title = j.get("title") or j.get("jobTitle") or ""
            link = j.get("jobUrl") or j.get("link") or j.get("url") or ""
            out.append(JobPosting(
                external_id=make_id("linkedin", link or title),
                title=title, company=j.get("companyName") or j.get("company") or "",
                url=link, source="apify_linkedin",
                location=j.get("location") or j.get("place"),
                description=_strip_html(j.get("description") or j.get("descriptionText")),
                kind=j.get("employmentType") or j.get("contractType")))
        return out


_PROVIDERS = [RemotiveProvider(), ArbeitnowProvider(), JobicyProvider(), TheMuseProvider(),
              GreenhouseProvider(), LeverProvider(), AdzunaProvider(), ApifyLinkedInProvider()]


def all_providers() -> list[JobProvider]:
    return list(_PROVIDERS)


def provider_status() -> list[dict]:
    return [{"name": p.name, "requires_key": p.requires_key, "available": p.available(),
             "env_key": p.env_key} for p in _PROVIDERS]
