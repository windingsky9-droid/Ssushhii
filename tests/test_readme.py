import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
LIVE = "https://raw.githack.com/windingsky9-droid/Ssushhii/main/"


def references():
    markdown = re.findall(r"\]\(([^)\s]+)\)", README)
    html = re.findall(r'(?:href|src)="([^"]+)"', README)
    return markdown + html


def anchor(heading):
    # GitHub's rule: lowercase, drop punctuation, spaces become hyphens
    return re.sub(r"[^a-z0-9 -]", "", heading.strip().lower()).replace(" ", "-")


def test_local_links_and_images_resolve():
    missing = []
    for ref in references():
        parts = urlsplit(ref)
        if parts.scheme or ref.startswith("#"):
            continue
        if parts.path and not (ROOT / unquote(parts.path)).exists():
            missing.append(ref)
    assert missing == []


def test_live_demo_links_open_files_in_this_repo():
    live = [ref for ref in references() if ref.startswith(LIVE)]
    assert len(live) >= 10
    missing = [ref for ref in live if not (ROOT / unquote(urlsplit(ref[len(LIVE):]).path)).is_file()]
    assert missing == []


def test_in_page_anchors_match_headings():
    headings = {anchor(h) for h in re.findall(r"^#{2,3} (.+)$", README, re.M)}
    targets = re.findall(r'href="#([^"]+)"', README) + re.findall(r"\]\(#([^)]+)\)", README)
    assert targets
    assert [t for t in targets if t not in headings] == []


def test_readme_images_have_alt_text():
    images = re.findall(r"<img\b[^>]*>", README)
    assert images
    assert [img for img in images if not re.search(r'alt="[^"]+"', img)] == []
