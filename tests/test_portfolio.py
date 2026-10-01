import re
from html.parser import HTMLParser
from pathlib import Path

PORTFOLIO = Path(__file__).resolve().parent.parent / "portfolio"
ALLOWED_EXTERNAL = (
    "https://cdnjs.cloudflare.com/",
    "https://fonts.googleapis.com",
    "https://fonts.gstatic.com",
    "https://github.com/windingsky9-droid/",
)


class _References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ("href", "src", "srcset") and value:
                self.refs.append(value)


def _pages():
    return [PORTFOLIO / "index.html", *sorted((PORTFOLIO / "demos").glob("*.html"))]


def _refs(page):
    parser = _References()
    parser.feed(page.read_text(encoding="utf-8"))
    return parser.refs


def test_local_references_resolve():
    for page in _pages():
        for ref in _refs(page):
            if ref.startswith(("#", "mailto:", "https://")):
                continue
            target = (page.parent / ref.split("#")[0]).resolve()
            assert target.exists(), f"{page.name} references missing file {ref}"


def test_external_references_are_allowlisted():
    for page in _pages():
        for ref in _refs(page):
            if ref.startswith("http"):
                assert ref.startswith(ALLOWED_EXTERNAL), f"{page.name} loads {ref}"


def test_workflow_demo_uses_synthetic_contacts_only():
    html = (PORTFOLIO / "demos" / "workflow-constellation.html").read_text(encoding="utf-8")
    emails = set(re.findall(r"[\w.+-]+@[\w-]+(?:\.[A-Za-z]{2,})+", html))
    assert emails, "expected sample customer addresses in the synthetic run"
    assert all(email.endswith("@example.com") for email in emails)


def test_demos_label_their_data_as_synthetic():
    for page in sorted((PORTFOLIO / "demos").glob("*.html")):
        assert "synthetic" in page.read_text(encoding="utf-8").lower(), page.name
