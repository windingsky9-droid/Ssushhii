import hashlib
import os
import re
from typing import Any, Protocol

from src.factorweave_client import FactorWeaveClient

_TICKER_RE = re.compile(r"^[A-Z0-9][A-Z0-9.\-]{0,9}$")
_COMPARABLES = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL"]


def normalize_ticker(value: str) -> str:
    ticker = (value or "").strip().upper()
    if not _TICKER_RE.fullmatch(ticker):
        raise ValueError("Enter a ticker using letters, numbers, dots, or hyphens.")
    return ticker


class ResearchProvider(Protocol):
    def research(self, ticker: str) -> dict[str, Any]: ...


class DemoResearchProvider:
    def _score(self, ticker: str, salt: str, low: int, high: int) -> int:
        digest = hashlib.sha256(f"{ticker}:{salt}".encode()).digest()
        return low + int.from_bytes(digest[:2], "big") % (high - low + 1)

    def research(self, ticker: str) -> dict[str, Any]:
        ticker = normalize_ticker(ticker)
        composite = self._score(ticker, "composite", 38, 92)
        momentum = self._score(ticker, "momentum", 30, 88)
        rsi = self._score(ticker, "rsi", 34, 72)
        realized_vol = self._score(ticker, "vol", 14, 48) / 100
        beta = self._score(ticker, "beta", 55, 155) / 100
        peers = [symbol for symbol in _COMPARABLES if symbol != ticker][:4]
        posture = "Constructive" if composite >= 70 else "Mixed" if composite >= 50 else "Defensive"
        return {
            "ticker": ticker,
            "source": "demo",
            "source_label": "Deterministic demo data",
            "as_of": "Synthetic snapshot — not live market data",
            "composite_score": composite,
            "posture": posture,
            "summary": f"{ticker} shows a {posture.lower()} demo factor profile. Use live mode for current research.",
            "metrics": {
                "momentum": momentum,
                "rsi": rsi,
                "realized_vol": realized_vol,
                "beta": beta,
            },
            "market": {
                "regime": "Balanced demo regime",
                "volatility": "Normal",
                "note": "Illustrative context for product evaluation only.",
            },
            "comparables": peers,
        }


class FactorWeaveResearchProvider:
    def __init__(self, client: FactorWeaveClient | None = None):
        self.client = client or FactorWeaveClient()

    def research(self, ticker: str) -> dict[str, Any]:
        ticker = normalize_ticker(ticker)
        features = self.client.features(ticker)
        market = self.client.market_context()
        similar = self.client.similar(ticker, limit=4)
        score = features.get("q_comp_score", features.get("comp_score", 0))
        if isinstance(score, (int, float)) and 0 <= score <= 1:
            score = round(score * 100)
        peers = []
        for item in similar.get("results", similar.get("rows", [])) if isinstance(similar, dict) else []:
            symbol = item.get("ticker") if isinstance(item, dict) else None
            if symbol and symbol != ticker:
                peers.append(symbol)
        return {
            "ticker": ticker,
            "source": "factorweave",
            "source_label": "Live Factor Weave",
            "as_of": features.get("date", "Latest available Factor Weave snapshot"),
            "composite_score": score,
            "posture": "Research snapshot",
            "summary": "Live factor snapshot supplied by Factor Weave. Interpret as research, not personalized advice.",
            "metrics": {
                "momentum": features.get("mom"),
                "rsi": features.get("rsi"),
                "realized_vol": features.get("vol_real_20d"),
                "beta": features.get("beta_spy"),
            },
            "market": market if isinstance(market, dict) else {"note": "Market context unavailable"},
            "comparables": peers[:4],
        }


def get_research_provider() -> ResearchProvider:
    if os.getenv("FACTORWEAVE_API_KEY"):
        return FactorWeaveResearchProvider()
    return DemoResearchProvider()
