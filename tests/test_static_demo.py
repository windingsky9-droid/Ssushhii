import json

from scripts.build_static_demo import TICKERS, build_static_demo
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

    blob = "".join(
        p.read_text(encoding="utf-8") for p in tmp_path.rglob("*") if p.is_file()
    ).lower()
    assert "fw_live_" not in blob
    assert "factorweave_api_key" not in blob
    assert "sk_live" not in blob
