"""Populate the jobs board from the sourcing engine (free providers by default).

    python scripts/source_jobs.py            # source + upsert into the platform DB
    python scripts/source_jobs.py --status   # just show provider availability
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pricinglibrary_rag import jobs_sourcing as js
from pricinglibrary_rag.factory import build_services
from pricinglibrary_rag.platform_store import PlatformStore


def main(argv):
    store = PlatformStore(build_services().settings.db_path)
    if "--status" in argv:
        print(json.dumps({"providers": js.provider_status(),
                          "counts": store.jobs_source_counts()}, indent=2))
        return 0
    report = js.source_jobs(store)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
