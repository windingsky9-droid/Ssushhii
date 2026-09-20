"""Pre-render the demo-mode app into a static site that needs no server.

Unlike ``build_public_demo.py``, which reimplements the scoring in hand-written
JavaScript, this builder calls ``DemoResearchProvider`` and writes its actual
output to per-ticker JSON files. The static build therefore cannot disagree
with the app: the numbers are produced by the same code path.

    python scripts/build_static_demo.py [output_dir]

Output (default ``static-demo/``) is plain files — upload them to any static
host. Deployed at <https://market-observatory.upfling.site>.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pricing import public_pricing  # noqa: E402
from src.research import DemoResearchProvider, normalize_ticker  # noqa: E402

TICKERS = [
    "SPY", "QQQ", "DIA", "IWM", "VTI",
    "AAPL", "MSFT", "NVDA", "AMZN", "META",
    "GOOGL", "TSLA", "AMD", "NFLX", "JPM",
    "V", "COST", "AVGO", "INTC", "DIS",
]

# app.js talks to the Flask routes. These are the only two call sites that need
# rewriting for a static host; both are asserted so an upstream edit fails the
# build loudly instead of shipping a demo that silently cannot load data.
LIVE_RESEARCH_FETCH = (
    'const response = await fetch(`/api/research?ticker=${encodeURIComponent(ticker)}`);\n'
    '    const body = await response.json();\n'
    '    if (!response.ok) throw new Error(body.error || "Research request failed.");'
)
STATIC_RESEARCH_FETCH = """const symbol = String(ticker || "").trim().toUpperCase();
    const response = await fetch(`api/research/${encodeURIComponent(symbol)}.json`);
    if (!response.ok) throw new Error(`${symbol} is not in this static demo. Available: ${AVAILABLE.join(", ")}`);
    const body = await response.json();"""

LIVE_CONFIG_FETCH = 'fetch("/api/config")'
STATIC_CONFIG_FETCH = 'fetch("api/config.json")'

JINJA_STATIC_URL = re.compile(r"\{\{\s*url_for\('static',\s*filename='([^']+)'\)\s*\}\}")


def _render_index() -> str:
    """Resolve the template's static URLs to relative paths."""
    html = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    html = JINJA_STATIC_URL.sub(r"\1", html)
    if "{{" in html or "{%" in html:
        raise SystemExit("templates/index.html has Jinja this builder cannot resolve statically")
    return html


def _render_app_js(tickers: list[str]) -> str:
    """Point app.js at the pre-rendered JSON instead of the Flask API."""
    js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    for needle in (LIVE_RESEARCH_FETCH, LIVE_CONFIG_FETCH):
        if needle not in js:
            raise SystemExit(f"static/app.js no longer contains the expected call site:\n{needle}")
    js = js.replace(LIVE_RESEARCH_FETCH, STATIC_RESEARCH_FETCH)
    js = js.replace(LIVE_CONFIG_FETCH, STATIC_CONFIG_FETCH)
    return f"const AVAILABLE = {json.dumps(tickers)};\n{js}"


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")


def build_static_demo(output_dir: Path, tickers: list[str] | None = None) -> None:
    tickers = [normalize_ticker(t) for t in (tickers or TICKERS)]
    research_dir = output_dir / "api" / "research"
    research_dir.mkdir(parents=True, exist_ok=True)

    provider = DemoResearchProvider()
    for ticker in tickers:
        _write_json(research_dir / f"{ticker}.json", provider.research(ticker))

    _write_json(output_dir / "api" / "config.json", public_pricing())
    _write_json(output_dir / "api" / "tickers.json", tickers)

    (output_dir / "index.html").write_text(_render_index(), encoding="utf-8")
    (output_dir / "styles.css").write_text(
        (ROOT / "static" / "styles.css").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (output_dir / "app.js").write_text(_render_app_js(tickers), encoding="utf-8")


if __name__ == "__main__":
    target = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "static-demo"
    build_static_demo(target)
    files = sorted(p for p in target.rglob("*") if p.is_file())
    print(f"Built {target} — {len(files)} files, {sum(p.stat().st_size for p in files)} bytes")
