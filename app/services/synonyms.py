from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional


_SPACE_RE = re.compile(r"\s+")


def normalize(text: str) -> str:
    return _SPACE_RE.sub(" ", text.strip().lower())


def _load_map() -> dict[str, str]:
    # Resolve project root relative to this file
    here = Path(__file__).resolve()
    repo_root = here.parents[2]
    path = repo_root / "taxonomy" / "synonyms.json"
    with path.open("r", encoding="utf-8") as f:
        data: dict[str, str] = json.load(f)
    # Normalize keys for robust matching
    return {normalize(k): v for k, v in data.items()}


_SYN_MAP = _load_map()


def canonicalize(text: str) -> Optional[str]:
    key = normalize(text)
    return _SYN_MAP.get(key)


def _synonyms_map() -> dict[str, str]:
    """Expose the normalized synonym mapping for read-only reuse."""
    return _SYN_MAP
