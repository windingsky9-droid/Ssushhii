import json
import re

from scripts.build_static_demo import SITE_URL, TICKERS, build_static_demo
from src.pricing import public_pricing
from src.research import DemoResearchProvider


def test_static_demo_matches_the_real_provider(tmp_path):
    """The whole point of this builder: the static site cannot disagree with the app.

    build_public_demo.py reimplements the scoring in JavaScript and drifts — it
    reports a different composite score, and sometimes the opposite posture, for
    the same ticker. Pre-rendering the real provider makes that impossible, so
    assert it rather than trusting it.
    """
    build_static_demo(tmp_path)
    provider = DemoResearchProvider()

    for ticker in TICKERS:
        rendered = json.loads((tmp_path / "api" / "research" / f"{ticker}.json").read_text(encoding="utf-8"))
        assert rendered == provider.research(ticker), f"{ticker} drifted from the provider"


def test_static_demo_needs_no_server(tmp_path):
    build_static_demo(tmp_path)

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    js = (tmp_path / "app.js").read_text(encoding="utf-8")

    assert "{{" not in html
    assert "url_for(" not in html

    # Absolute Flask routes would 404 on a static host.
    assert '"/api/' not in js
    assert "`/api/" not in js
    assert "api/research/" in js
    assert "api/config.json" in js


def test_static_demo_index_lists_exactly_what_it_ships(tmp_path):
    build_static_demo(tmp_path)

    listed = json.loads((tmp_path / "api" / "tickers.json").read_text(encoding="utf-8"))
    present = sorted(p.stem for p in (tmp_path / "api" / "research").glob("*.json"))

    assert sorted(listed) == present
    assert listed == TICKERS


def test_static_demo_ships_no_credentials_and_no_live_checkout(tmp_path):
    build_static_demo(tmp_path)

    config = json.loads((tmp_path / "api" / "config.json").read_text(encoding="utf-8"))
    assert config == public_pricing()

    for plan in config["plans"]:
        url = plan.get("checkout_url")
        if plan["price"] > 0:
            # A paid plan must stay disabled unless STRIPE_*_URL is deliberately set.
            assert not plan["checkout_enabled"], f"{plan['id']} would take payments from a static demo"
            assert url is None
        # The free plan's "checkout" is an in-page anchor; nothing may point off-site.
        assert url is None or url.startswith("#"), f"{plan['id']} ships an external checkout URL"

    # Read bytes, not text: the build ships a PNG. Decoding leniently still
    # catches an ASCII secret embedded in a binary, which text-only would miss.
    blob = "".join(
        p.read_bytes().decode("utf-8", errors="ignore") for p in tmp_path.rglob("*") if p.is_file()
    ).lower()
    assert "fw_live_" not in blob
    assert "factorweave_api_key" not in blob
    assert "sk_live" not in blob


def test_static_demo_unfurls_as_a_link_preview(tmp_path):
    """A pasted link must render as a card, not a bare grey URL.

    Unfurlers (Slack, Discord, WhatsApp, LinkedIn, iMessage) drop relative
    og:image/og:url values silently, so assert the absolute form specifically —
    a relative path would still "have the tag" and still show nothing.
    """
    build_static_demo(tmp_path)
    html = (tmp_path / "index.html").read_text(encoding="utf-8")

    def meta(attr: str, key: str) -> str:
        match = re.search(rf'<meta {attr}="{re.escape(key)}" content="([^"]*)">', html)
        assert match, f"missing {key}"
        return match.group(1)

    for prop in ("og:title", "og:description", "og:type", "og:url", "og:image"):
        assert meta("property", prop), f"{prop} is empty"
    assert meta("name", "twitter:card") == "summary_large_image"

    # Assert per-tag, not "the absolute URL appears somewhere in the file":
    # twitter:image alone would satisfy a whole-document search while og:image
    # stayed relative and every unfurler showed nothing.
    assert meta("property", "og:image") == f"{SITE_URL}/og-card.png"
    assert meta("name", "twitter:image") == f"{SITE_URL}/og-card.png"
    assert meta("property", "og:url") == f"{SITE_URL}/"
    assert 'rel="icon"' in html

    # The referenced assets must actually ship, or the card renders blank.
    assert (tmp_path / "og-card.png").is_file()
    assert (tmp_path / "favicon.svg").is_file()


def test_static_demo_preview_image_is_a_valid_1200x630_png(tmp_path):
    """Unfurlers reject the wrong aspect ratio, and a truncated file shows nothing."""
    build_static_demo(tmp_path)
    data = (tmp_path / "og-card.png").read_bytes()

    assert data[:8] == b"\x89PNG\r\n\x1a\n", "og-card.png is not a PNG"
    # IHDR width/height are big-endian uint32 at fixed offsets in the first chunk.
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    assert (width, height) == (1200, 630), f"expected 1200x630, got {width}x{height}"


def test_static_demo_base_url_is_configurable(tmp_path):
    """Deploying elsewhere must not silently keep pointing at the old host."""
    build_static_demo(tmp_path, base_url="https://example.test/")
    html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'content="https://example.test/og-card.png"' in html
    assert SITE_URL not in html
