import os
from typing import Any

import requests

DEFAULT_BASE_URL = "https://factorweave.com/api"


class FactorWeaveClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or os.getenv("FACTORWEAVE_API_KEY")
        self.base_url = (base_url or os.getenv("FACTORWEAVE_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        if not self.api_key:
            raise RuntimeError("Set FACTORWEAVE_API_KEY in your environment or .env file.")

    @property
    def headers(self) -> dict[str, str]:
        return {"X-API-Key": self.api_key, "Accept": "application/json"}

    def _get(self, path: str, **params: Any) -> Any:
        response = requests.get(
            f"{self.base_url}/{path.lstrip('/')}",
            headers=self.headers,
            params={k: v for k, v in params.items() if v is not None},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def features(self, ticker: str) -> Any:
        return self._get(f"features/{ticker.upper()}")

    def top(self, factor: str, n: int = 25) -> Any:
        return self._get("top", factor=factor, n=n)

    def similar(
        self,
        ticker: str,
        method: str = "cosine",
        limit: int = 10,
        min_lookback_days: int = 30,
    ) -> Any:
        return self._get(
            f"vector-search/similar/{ticker.upper()}",
            method=method,
            limit=limit,
            min_lookback_days=min_lookback_days,
        )

    def market_context(self) -> Any:
        return self._get("market-context")
