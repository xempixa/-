from __future__ import annotations

import json
import os
from pathlib import Path

from app.config import settings


def export_netscape_cookies(
    storage_state_path: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    state_path = storage_state_path or settings.storage_state_path
    output = output_path or (settings.data_dir / "cookies.txt")

    data = json.loads(state_path.read_text(encoding="utf-8"))
    cookies = data.get("cookies", [])

    lines = [
        "# Netscape HTTP Cookie File",
        "# This file is generated from Playwright storage_state.json",
    ]

    for c in cookies:
        domain = c.get("domain", "")
        include_subdomain = "TRUE" if domain.startswith(".") else "FALSE"
        path = c.get("path", "/")
        secure = "TRUE" if c.get("secure") else "FALSE"
        expires = str(int(c.get("expires", 0))) if c.get("expires") else "0"
        name = c.get("name", "")
        value = c.get("value", "")

        if not domain or not name:
            continue

        lines.append("\t".join([domain, include_subdomain, path, secure, expires, name, value]))

    output.write_text("\n".join(lines), encoding="utf-8", newline="\n")

    try:
        os.chmod(output, 0o600)
    except OSError:
        pass

    return output
