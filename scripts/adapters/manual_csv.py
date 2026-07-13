"""Adapter for licensed or manually maintained quarterly credit indicators.

Expected CSV columns: series_id,value,observation_date,source
The adapter deliberately does not invent a value when no licensed input exists.
"""
from __future__ import annotations

import csv
from pathlib import Path


def read_latest(path: Path, series_id: str) -> dict[str, str] | None:
    if not path.exists():
        return None
    with path.open(encoding="utf-8", newline="") as stream:
        rows = [row for row in csv.DictReader(stream) if row.get("series_id") == series_id]
    return max(rows, key=lambda row: row.get("observation_date", ""), default=None)
