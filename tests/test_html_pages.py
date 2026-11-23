import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted(
    page
    for folder in ("portfolio", "showcase", "public-demo", "templates")
    for page in (ROOT / folder).rglob("*.html")
)
# Text that once leaked into pages from pasted tool output. Anything before the
# doctype also drops the browser into quirks mode and shifts the layout.
PASTED_OUTPUT = re.compile(r"^\[Reading \d+ lines from start|\[executed on device:", re.M)


def _page_id(page):
    return str(page.relative_to(ROOT))


def test_pages_were_found():
    assert len(PAGES) >= 10


@pytest.mark.parametrize("page", PAGES, ids=_page_id)
def test_page_starts_with_doctype(page):
    text = page.read_text(encoding="utf-8").lstrip("﻿")
    assert text.lower().startswith("<!doctype html>")


@pytest.mark.parametrize("page", PAGES, ids=_page_id)
def test_page_has_no_pasted_tool_output(page):
    text = page.read_text(encoding="utf-8")
    assert PASTED_OUTPUT.search(text) is None
    assert text.rstrip().lower().endswith("</html>")
