"""Single integration seam to the sibling lab repos.

The live backend keeps the two research projects as the *source of truth* (no
forking, no vendored copies) and reaches them through one path-setup point:

    * VolSurface Live  ->  ``QUANT_VOL_STAY/backend``      (package ``app``)
    * Trading engine   ->  ``TRADING/trading_engine``      (package ``src``)

Paths are discovered relative to this file's repo, then overridable by env
(``TPL_VOLSURFACE_ROOT`` / ``TPL_TRADING_ROOT``) for the live deployment where
the three folders may sit elsewhere. Every accessor degrades gracefully: if a
repo is absent the caller gets ``None`` and the backend stays up.
"""
from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path

# …/documents/THEPRICINGLIBRARY/Tools/pricinglibrary_rag_backend/pricinglibrary_rag/integrations.py
# parents[4] == …/documents  (the common parent of the 3 sibling projects)
_DOCS = Path(__file__).resolve().parents[4]


def _candidates(env: str, *rel: str) -> list[Path]:
    out: list[Path] = []
    if os.environ.get(env):
        out.append(Path(os.environ[env]))
    out.extend(_DOCS / r for r in rel)
    return out


def _ensure_on_path(env: str, *rel: str) -> Path | None:
    for c in _candidates(env, *rel):
        if c.exists():
            p = str(c)
            if p not in sys.path:
                sys.path.insert(0, p)
            return c
    return None


@lru_cache(maxsize=1)
def volsurface_root() -> Path | None:
    return _ensure_on_path("TPL_VOLSURFACE_ROOT", "QUANT_VOL_STAY/backend")


@lru_cache(maxsize=1)
def trading_root() -> Path | None:
    return _ensure_on_path("TPL_TRADING_ROOT", "TRADING/trading_engine")


def status() -> dict:
    vs, tr = volsurface_root(), trading_root()
    return {
        "volsurface": {"present": vs is not None, "root": str(vs) if vs else None},
        "trading": {"present": tr is not None, "root": str(tr) if tr else None},
    }
