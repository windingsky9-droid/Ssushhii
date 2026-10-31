"""Check that every local link and asset in the portfolio pages exists.

Usage:
    python scripts/check_portfolio.py

Exits non-zero and lists each broken reference when a page points at a file
that is missing, so a renamed still or demo is caught before it ships.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = ROOT / "portfolio"
REFERENCE = re.compile(r"""(?:href|src)\s*=\s*["']([^"']+)["']""")


def local_references(page: Path) -> list[str]:
    refs = []
    for raw in REFERENCE.findall(page.read_text(encoding="utf-8")):
        parts = urlsplit(raw)
        if parts.scheme or raw.startswith(("#", "//")):
            continue
        if parts.path:
            refs.append(unquote(parts.path))
    return refs


def broken_references(folder: Path = PORTFOLIO) -> list[str]:
    problems = []
    for page in sorted(folder.rglob("*.html")):
        for ref in local_references(page):
            target = (page.parent / ref).resolve()
            if not target.exists():
                problems.append(f"{page.relative_to(folder)} -> {ref}")
    return problems


def main() -> int:
    problems = broken_references()
    if problems:
        print("Broken portfolio references:")
        for line in problems:
            print(f"  {line}")
        return 1
    print("All portfolio references resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
