import httpx
import pytest
from unittest.mock import AsyncMock, patch
from src.market_data import MarketDataClient
from src.models import Signal

@pytest.mark.asyncio
async def test_fetch_fear_greed():
    mock_response = httpx.Response(
        200,
        json={"data": {"value": 18, "value_classification": "Extreme Fear"}},
        request=httpx.Request("GET", "https://example.com"),
    )
    with patch("src.market_data.httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
        client = MarketDataClient(api_key="test-key")
        result = await client.fetch_fear_greed()
        assert result["value"] == 18

@pytest.mark.asyncio
async def test_fetch_price():
    mock_response = httpx.Response(
        200,
        json={"data": {"CAKE": {"quote": {"USD": {"price": 2.45, "percent_change_24h": -6.2}}}}},
        request=httpx.Request("GET", "https://example.com"),
    )
    with patch("src.market_data.httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
        client = MarketDataClient(api_key="test-key")
        price, change = await client.fetch_price("CAKE")
        assert price == 2.45
        assert change == -6.2

@pytest.mark.asyncio
async def test_build_signal():
    client = MarketDataClient(api_key="test-key")
    with patch.object(client, "fetch_fear_greed", new_callable=AsyncMock, return_value={"value": 18}):
        with patch.object(client, "fetch_price", new_callable=AsyncMock, return_value=(2.45, -6.2)):
            signal = await client.build_signal("CAKE")
            assert isinstance(signal, Signal)
            assert signal.token == "CAKE"
            assert signal.fear_greed_index == 18
            assert signal.price_change_pct == -6.2
