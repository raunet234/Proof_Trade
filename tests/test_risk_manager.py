from src.risk_manager import RiskManager
from src.models import Decision, Action
from src.portfolio import Portfolio
from src.config import Config

def make_config(**overrides):
    defaults = dict(
        trading_mode="paper", cmc_api_key="k", anthropic_api_key="k",
        tw_access_id="", tw_hmac_secret="", wallet_password="", private_key="",
        initial_capital=1000, max_trade_size=20, max_drawdown_pct=30,
        target_tokens=["CAKE", "BNB", "LINK"],
    )
    defaults.update(overrides)
    return Config(**defaults)

def test_valid_trade_passes():
    config = make_config()
    portfolio = Portfolio(initial_capital=1000.0)
    rm = RiskManager(config)
    decision = Decision(action=Action.BUY, token="CAKE", reason="dip", confidence=0.8)
    ok, reason = rm.check(decision, portfolio)
    assert ok is True

def test_token_not_on_allowlist():
    config = make_config()
    portfolio = Portfolio(initial_capital=1000.0)
    rm = RiskManager(config)
    decision = Decision(action=Action.BUY, token="SCAMCOIN", reason="yolo", confidence=0.9)
    ok, reason = rm.check(decision, portfolio)
    assert ok is False
    assert "allowlist" in reason.lower()

def test_drawdown_above_30_blocks():
    config = make_config()
    portfolio = Portfolio(initial_capital=1000.0)
    portfolio.cash = 690.0  # 31% drawdown
    portfolio.peak_value = 1000.0
    rm = RiskManager(config)
    decision = Decision(action=Action.BUY, token="CAKE", reason="dip", confidence=0.8)
    ok, reason = rm.check(decision, portfolio)
    assert ok is False
    assert "drawdown" in reason.lower()

def test_drawdown_25_to_29_forces_paper():
    config = make_config(trading_mode="live")
    portfolio = Portfolio(initial_capital=1000.0)
    portfolio.cash = 740.0  # 26% drawdown
    portfolio.peak_value = 1000.0
    rm = RiskManager(config)
    decision = Decision(action=Action.BUY, token="CAKE", reason="dip", confidence=0.8)
    ok, reason = rm.check(decision, portfolio)
    assert ok is True
    assert rm.force_paper is True

def test_hold_always_passes():
    config = make_config()
    portfolio = Portfolio(initial_capital=1000.0)
    rm = RiskManager(config)
    decision = Decision(action=Action.HOLD, token="CAKE", reason="wait", confidence=0.5)
    ok, reason = rm.check(decision, portfolio)
    assert ok is True

def test_insufficient_cash():
    config = make_config()
    portfolio = Portfolio(initial_capital=1000.0)
    portfolio.cash = 10.0  # less than max_trade_size of $20
    rm = RiskManager(config)
    decision = Decision(action=Action.BUY, token="CAKE", reason="dip", confidence=0.8)
    ok, reason = rm.check(decision, portfolio)
    assert ok is False
    assert "cash" in reason.lower()
