from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "portfolio" / "skill-value.html"


def test_skill_value_dashboard_is_present_and_evidence_first():
    html = DASHBOARD.read_text(encoding="utf-8")

    assert "<title>SUSHI" in html
    assert "MODELED ANNUAL GROSS BILLINGS" in html
    assert "not salary or earnings" in html.lower()
    assert "Unverified" in html
    assert "CODE FOUND" in html
    assert "TO PROVE" in html
    assert "id=\"rate\"" in html
    assert "id=\"hours\"" in html
    assert "id=\"weeks\"" in html
    assert "aria-pressed" in html
    assert "prefers-reduced-motion" in html

    # The public showcase must not expose the private relationship/birth dataset.
    assert "Ismael" not in html
    assert "Guadalajara" not in html
    assert "2001-10-16" not in html


def test_skill_value_dashboard_uses_existing_portfolio_assets():
    assert (ROOT / "portfolio" / "media" / "astral-vault-v11-showpiece.png").is_file()
    assert (ROOT / "portfolio" / "demos" / "celestial-observatory-public.html").is_file()
    assert (ROOT / "showcase" / "SUSHIR_HALO_TACTICAL_COMMAND_CENTER_V12_CINEMATIC_OPERATIONS.html").is_file()
    assert (ROOT / "docs" / "services" / "flask-api-fix.md").is_file()
    assert 'href="skill-value.html"' in (ROOT / "portfolio" / "index.html").read_text(encoding="utf-8")
