import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_portfolio", ROOT / "scripts" / "check_portfolio.py")
check_portfolio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_portfolio)


def test_portfolio_references_resolve():
    assert check_portfolio.broken_references() == []


def test_checker_reports_missing_asset(tmp_path):
    (tmp_path / "index.html").write_text('<img src="media/missing.jpg"><a href="https://example.com">x</a><a href="#top">y</a>')
    assert check_portfolio.broken_references(tmp_path) == ["index.html -> media/missing.jpg"]


def test_support_links_stay_owner_configured():
    config = (ROOT / "portfolio" / "site-config.js").read_text(encoding="utf-8")
    assert "supportLinks" in config
    index = (ROOT / "portfolio" / "index.html").read_text(encoding="utf-8")
    assert '<section id="support" class="section support" hidden>' in index
