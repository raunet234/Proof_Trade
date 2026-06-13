from __future__ import annotations
import httpx
from src.models import Signal

CMC_BASE = "https://pro-api.coinmarketcap.com"


class MarketDataClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "X-CMC_PRO_API_KEY": api_key,
            "Accept": "application/json",
        }

    async def fetch_fear_greed(self) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{CMC_BASE}/v3/fear-and-greed/latest",
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()["data"]

    async def fetch_price(self, symbol: str) -> tuple[float, float]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{CMC_BASE}/v2/cryptocurrency/quotes/latest",
                headers=self.headers,
                params={"symbol": symbol, "convert": "USD"},
            )
            resp.raise_for_status()
            data = resp.json()["data"][symbol]
            if isinstance(data, list):
                data = data[0]
            quote = data["quote"]["USD"]
            return quote["price"], quote["percent_change_24h"]

    async def build_signal(self, token: str) -> Signal:
        fg = await self.fetch_fear_greed()
        price, change = await self.fetch_price(token)
        return Signal(
            fear_greed_index=fg["value"],
            price_change_pct=change,
            token=token,
            current_price=price,
        )
