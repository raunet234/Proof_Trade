import pytest
from unittest.mock import patch, MagicMock
from src.executor import Executor
from src.models import Decision, Action, Trade

def test_paper_trade_buy():
    executor = Executor(is_paper=True)
    decision = Decision(action=Action.BUY, token="CAKE", reason="dip", confidence=0.8)
    trade = executor.execute(decision, current_price=2.45, size_usd=20.0)
    assert isinstance(trade, Trade)
    assert trade.is_paper is True
    assert trade.token == "CAKE"
    assert trade.price == 2.45
    assert trade.tx_hash is None

def test_paper_trade_sell():
    executor = Executor(is_paper=True)
    decision = Decision(action=Action.SELL, token="CAKE", reason="bounce", confidence=0.7)
    trade = executor.execute(decision, current_price=2.75, size_usd=22.0)
    assert trade.action == Action.SELL
    assert trade.is_paper is True

def test_hold_returns_none():
    executor = Executor(is_paper=True)
    decision = Decision(action=Action.HOLD, token="CAKE", reason="wait", confidence=0.5)
    trade = executor.execute(decision, current_price=2.45, size_usd=0)
    assert trade is None

def test_live_trade_calls_twak():
    executor = Executor(is_paper=False)
    decision = Decision(action=Action.BUY, token="CAKE", reason="dip", confidence=0.8)

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = '{"txHash": "0xabc123"}'

    with patch("src.executor.subprocess.run", return_value=mock_result) as mock_run:
        trade = executor.execute(decision, current_price=2.45, size_usd=20.0)
        assert trade.is_paper is False
        assert trade.tx_hash == "0xabc123"
        # Verify the correct TWAK swap syntax was used
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "twak"
        assert call_args[1] == "swap"
        assert "20.0" in call_args[2] or call_args[2] == "20.0"
        # For BUY: swap USDT -> TOKEN, so args should be: twak swap <amount> USDT CAKE --chain bsc
        assert "USDT" in call_args
        assert "CAKE" in call_args
