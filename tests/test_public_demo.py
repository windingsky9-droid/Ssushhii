from pathlib import Path

from scripts.build_public_demo import build_public_demo


def test_public_demo_is_static_and_secret_free(tmp_path):
    build_public_demo(tmp_path)

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    js = (tmp_path / "app.js").read_text(encoding="utf-8")
    css = (tmp_path / "styles.css").read_text(encoding="utf-8")

    assert "Market Observatory" in html
    assert "not investment advice" in html.lower()
    assert "{{" not in html
    assert "url_for(" not in html
    assert "/api/research" not in js
    assert "/api/config" not in js
    assert "fw_live_" not in (html + js + css).lower()
    assert "synthetic" in js.lower()
