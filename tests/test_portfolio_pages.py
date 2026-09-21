"""Guards for the public portfolio pages.

Every assertion here is a bug that actually shipped and sat live for a while.
They are all cheap, and none of them needs a browser: the failures were visible
in a rendered page but provable from the source.
"""
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = ROOT / "portfolio"
PAGES = sorted(PORTFOLIO.rglob("index.html"))

NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def test_pages_were_found():
    """A glob that silently matches nothing would make every test below vacuous."""
    assert len(PAGES) >= 4, [str(p) for p in PAGES]


class _NestedAnchors(HTMLParser):
    """The homepage shipped an <a> inside an <a>.

    That is a parse error, and the recovery is not benign: the browser closes the
    outer anchor and reparents what follows into the next open element. Here that
    was .work-copy, which is position:absolute — so the entire work grid rendered
    on top of the hero. It looked like a CSS bug and it was a markup bug.
    """

    def __init__(self):
        super().__init__()
        self.depth = 0
        self.nested = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        if self.depth:
            self.nested.append((self.getpos(), dict(attrs).get("href")))
        self.depth += 1

    def handle_endtag(self, tag):
        if tag == "a" and self.depth:
            self.depth -= 1


def test_no_anchor_nested_in_an_anchor():
    for page in PAGES:
        parser = _NestedAnchors()
        parser.feed(page.read_text(encoding="utf-8"))
        rel = page.relative_to(ROOT)
        assert not parser.nested, f"{rel}: <a> inside <a> at {parser.nested}"


def test_pages_do_not_hotlink_their_own_repo():
    """The hero was a 4.2 MB PNG served from raw.githubusercontent.com.

    That host is not a CDN for site assets: it sets max-age=300, so every visitor
    re-fetched it every five minutes, and the page's appearance depended on the
    repo's default branch staying public.
    """
    for page in PAGES:
        text = page.read_text(encoding="utf-8")
        assert "raw.githubusercontent.com" not in text, page.relative_to(ROOT)


def test_configurator_copy_matches_the_products_it_ships():
    """"Four completely different products" sat above a five-product picker.

    Both link-preview descriptions said it too, so that was what a shared URL
    showed. Check the prose against the picker the visitor actually sees.
    """
    page = PORTFOLIO / "3d" / "index.html"
    text = page.read_text(encoding="utf-8")
    shipped = len(re.findall(r"label: '([^']+)'", text))
    assert shipped, "found no product labels - has the PRODUCTS shape changed?"

    claims = re.findall(r"\b(" + "|".join(NUMBER_WORDS) + r") (?:completely different )?products\b",
                        text, re.IGNORECASE)
    assert claims, "no product count claimed in the copy; did the wording change?"
    for claim in claims:
        assert NUMBER_WORDS[claim.lower()] == shipped, (
            f"copy says {claim} products, page ships {shipped}")


def test_render_gallery_is_generated_not_hand_edited():
    """The gallery read "384 renders, 4 products" for a while after the manifest said 480.

    The meta description had been updated by hand and the visible header had not.
    Regenerating it from the committed pack assets is the only thing that keeps
    the two in step, so assert the committed page is exactly what the generator
    produces.
    """
    shipped = PORTFOLIO / "renders" / "index.html"
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "index.html"
        subprocess.run(
            [sys.executable, str(ROOT / "tools/render-farm/build_gallery.py"),
             str(ROOT / "products/3d-render-pack"),
             str(PORTFOLIO / "renders/sample/manifest-sample.csv"),
             str(out)],
            check=True, capture_output=True, text=True)
        assert out.read_bytes() == shipped.read_bytes(), (
            "portfolio/renders/index.html differs from build_gallery.py output - "
            "regenerate it rather than editing it by hand")
