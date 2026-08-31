from app import create_app


class FakeProvider:
    def research(self, ticker):
        return {
            "ticker": ticker,
            "source": "demo",
            "source_label": "Demo",
            "as_of": "test",
            "composite_score": 72,
            "posture": "Constructive",
            "summary": "Test research",
            "metrics": {"momentum": 60, "rsi": 55, "realized_vol": 0.2, "beta": 1.0},
            "market": {"regime": "balanced"},
            "comparables": ["MSFT"],
        }


def client(provider=None):
    app = create_app(provider=provider or FakeProvider())
    app.config.update(TESTING=True)
    return app.test_client()


def test_health_endpoint():
    response = client().get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_research_endpoint_normalizes_ticker():
    response = client().get("/api/research?ticker= spy ")
    assert response.status_code == 200
    assert response.get_json()["ticker"] == "SPY"


def test_research_endpoint_rejects_invalid_ticker():
    response = client().get("/api/research?ticker=bad ticker!")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_research_endpoint_hides_provider_failure():
    class BrokenProvider:
        def research(self, ticker):
            raise RuntimeError("secret upstream details")

    response = client(BrokenProvider()).get("/api/research?ticker=SPY")
    assert response.status_code == 503
    body = response.get_json()
    assert body["error"] == "Research is temporarily unavailable."
    assert "secret" not in str(body).lower()


def test_config_disables_checkout_without_environment(monkeypatch):
    for name in ("STRIPE_PRO_URL", "STRIPE_CREATOR_URL"):
        monkeypatch.delenv(name, raising=False)
    response = client().get("/api/config")
    assert response.status_code == 200
    plans = {plan["id"]: plan for plan in response.get_json()["plans"]}
    assert plans["pro"]["checkout_enabled"] is False
    assert plans["creator"]["checkout_enabled"] is False
    assert plans["free"]["price"] == 0


def test_dashboard_renders_conversion_and_risk_elements():
    response = client().get("/")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Market Observatory" in html
    assert 'id="research-form"' in html
    assert 'id="source-badge"' in html
    assert 'id="pricing"' in html
    assert "not investment advice" in html.lower()


def test_dashboard_links_to_free_early_access_funnel():
    response = client().get("/")
    html = response.get_data(as_text=True)
    assert "Request early access" in html
    assert "issues/new?template=early-access.yml" in html


def test_dashboard_has_developer_service_request_cta():
    response = client().get("/")
    html = response.get_data(as_text=True)
    assert "Need this built for your project?" in html
    assert "issues/new?template=service-request.yml" in html
