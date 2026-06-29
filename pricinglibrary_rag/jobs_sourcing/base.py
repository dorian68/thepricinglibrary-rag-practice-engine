"""Contracts for the jobs sourcing engine.

Each provider returns ``JobPosting`` objects with a stable ``external_id`` (used
to dedupe across refreshes) and a real apply ``url``. Free, keyless providers
populate the board today (free plan); key-gated providers (Apify/LinkedIn,
Adzuna) light up when their env keys are set (paid enrichment later).
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class JobPosting:
    external_id: str
    title: str
    company: str
    url: str
    source: str
    location: str | None = None
    description: str | None = None
    tags: list[str] = field(default_factory=list)
    remote: bool = False
    kind: str | None = None  # full-time | internship | contract ...

    def to_store(self) -> dict:
        return {"external_id": self.external_id, "title": self.title[:240],
                "company": (self.company or "—")[:160], "location": self.location,
                "kind": self.kind, "tags": self.tags[:8], "description": (self.description or None),
                "url": self.url, "source": self.source, "remote": self.remote}


def make_id(source: str, *parts: str) -> str:
    raw = "|".join([source, *[p or "" for p in parts]])
    return f"{source}:{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:16]}"


def http_json(url: str, *, timeout: float = 20, headers: dict | None = None,
              method: str = "GET", body: dict | None = None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"User-Agent": "tpl-jobs/1.0",
                                          "Accept": "application/json", **(headers or {})})
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


class JobProvider(ABC):
    name: str = "provider"
    requires_key: bool = False
    env_key: str | None = None

    def api_key(self) -> str | None:
        return os.environ.get(self.env_key) if self.env_key else None

    def available(self) -> bool:
        return (not self.requires_key) or bool(self.api_key())

    @abstractmethod
    def fetch(self, *, query: str = "finance", limit: int = 50) -> list[JobPosting]:
        """Return raw postings (finance filtering happens in the pipeline)."""
