import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.decision_engine import DecisionEngine
from src.models import Signal, Decision, Action

@pytest.mark.asyncio
async def test_decide_buy_signal():
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text='{"action": "BUY", "reason": "5% drop with extreme fear", "confidence": 0.85}')]
    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_message)
    with patch("src.decision_engine.anthropic.AsyncAnthropic", return_value=mock_client):
        engine = DecisionEngine(api_key="test-key")
        signal = Signal(fear_greed_index=18, price_change_pct=-6.2, token="CAKE", current_price=2.45)
        decision = await engine.decide(signal)
        assert isinstance(decision, Decision)
        assert decision.action == Action.BUY
        assert decision.token == "CAKE"

@pytest.mark.asyncio
async def test_decide_hold_signal():
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text='{"action": "HOLD", "reason": "no clear signal", "confidence": 0.5}')]
    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_message)
    with patch("src.decision_engine.anthropic.AsyncAnthropic", return_value=mock_client):
        engine = DecisionEngine(api_key="test-key")
        signal = Signal(fear_greed_index=50, price_change_pct=-1.0, token="CAKE", current_price=2.45)
        decision = await engine.decide(signal)
        assert decision.action == Action.HOLD

@pytest.mark.asyncio
async def test_decide_returns_hold_on_parse_error():
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="not valid json")]
    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_message)
    with patch("src.decision_engine.anthropic.AsyncAnthropic", return_value=mock_client):
        engine = DecisionEngine(api_key="test-key")
        signal = Signal(fear_greed_index=50, price_change_pct=-1.0, token="CAKE", current_price=2.45)
        decision = await engine.decide(signal)
        assert decision.action == Action.HOLD
