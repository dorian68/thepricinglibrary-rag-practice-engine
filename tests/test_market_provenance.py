from __future__ import annotations

import pandas as pd

from pricinglibrary_rag.marketdata import history_provenance


def test_history_provenance_exposes_source_date_unit_and_limits() -> None:
    frame = pd.DataFrame(
        {"close": [4.2, 4.25]},
        index=pd.to_datetime(["2026-06-24", "2026-06-25"]),
    )
    provenance = history_provenance("DGS10", "fred", frame, cache_hit=True)
    assert provenance["source"] == "fred:DGS10"
    assert provenance["status"] == "cached_snapshot"
    assert provenance["as_of_date"] == "2026-06-25"
    assert provenance["unit"] == "percent yield"
    assert "not an executable quote or investment signal" in provenance["limitations"]

