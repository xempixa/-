from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


def export_csv(rows: Iterable[dict], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    materialized_rows = list(rows)
    if not materialized_rows:
        path.write_text("", encoding="utf-8")
        return path

    fieldnames = list(materialized_rows[0].keys())
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(materialized_rows)

    return path
