from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def export_json(rows: Iterable[dict], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(list(rows), f, ensure_ascii=False, indent=2)

    return path
