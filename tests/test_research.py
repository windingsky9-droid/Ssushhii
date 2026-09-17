import pytest

from src.research import (
    DemoResearchProvider,
    FactorWeaveResearchProvider,
    get_research_provider,
    normalize_ticker,
)


def test_normalize_ticker_trims_and_uppercases():
    assert normalize_ticker(" spy ") == "SPY"


def test_normalize_ticker_rejects_unsafe_characters():
    with pytest.raises(ValueError, match="ticker"):
        normalize_ticker("SPY;DROP")


def test_demo_research_is_deterministic_and_labeled():
    provider = DemoResearchProvider()
    first = provider.research("AAPL")
    second = provider.research("AAPL")

    assert first == second
    assert first["ticker"] == "AAPL"
    assert first["source"] == "demo"
    assert 0 <= first["composite_score"] <= 100
    assert set(first["metrics"]) >= {"momentum", "rsi", "realized_vol", "beta"}


def test_provider_selection_uses_demo_without_key(monkeypatch):
    monkeypatch.delenv("FACTORWEAVE_API_KEY", raising=False)
    assert isinstance(get_research_provider(), DemoResearchProvider)


def test_provider_selection_uses_factorweave_with_key(monkeypatch):
    monkeypatch.setenv("FACTORWEAVE_API_KEY", "fw_live_test_only")
    assert isinstance(get_research_provider(), FactorWeaveResearchProvider)


def test_factorweave_provider_maps_live_payload_without_exposing_key():
    class FakeClient:
        def features(self, ticker):
            return {"ticker": ticker, "comp_score": 0.61, "mom": 0.12, "rsi": 58, "vol_real_20d": 0.24, "beta_spy": 1.08}

        def market_context(self):
            return {"regime": "risk_on", "vix": 17.5}

        def similar(self, ticker, limit=4):
            return {"results": [{"ticker": "MSFT"}, {"ticker": "NVDA"}]}

    result = FactorWeaveResearchProvider(FakeClient()).research("aapl")
    assert result["ticker"] == "AAPL"
    assert result["source"] == "factorweave"
    assert result["composite_score"] == 61
    assert result["comparables"] == ["MSFT", "NVDA"]
    assert "api_key" not in str(result).lower()
