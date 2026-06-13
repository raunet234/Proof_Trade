from src.portfolio import Portfolio
from src.models import Action, Trade

def test_portfolio_initial_state():
    p = Portfolio(initial_capital=1000.0)
    assert p.cash == 1000.0
    assert p.positions == {}
    assert p.drawdown_pct == 0.0

def test_portfolio_buy():
    p = Portfolio(initial_capital=1000.0)
    trade = Trade(token="CAKE", action=Action.BUY, price=2.50, size_usd=20.0, is_paper=True)
    p.record_trade(trade)
    assert p.cash == 980.0
    assert "CAKE" in p.positions
    assert p.positions["CAKE"].quantity == 8.0

def test_portfolio_sell():
    p = Portfolio(initial_capital=1000.0)
    buy = Trade(token="CAKE", action=Action.BUY, price=2.50, size_usd=20.0, is_paper=True)
    p.record_trade(buy)
    sell = Trade(token="CAKE", action=Action.SELL, price=2.75, size_usd=22.0, is_paper=True)
    p.record_trade(sell)
    assert "CAKE" not in p.positions
    assert p.cash > 1000.0

def test_portfolio_drawdown():
    p = Portfolio(initial_capital=1000.0)
    p.cash = 750.0  # simulate losses
    assert p.drawdown_pct == 25.0

def test_portfolio_peak_tracking():
    p = Portfolio(initial_capital=1000.0)
    p.cash = 1100.0  # gains
    p.update_peak()
    p.cash = 900.0  # drop from peak
    # drawdown from peak of 1100
    assert abs(p.drawdown_pct - 18.18) < 0.1

def test_portfolio_trade_log():
    p = Portfolio(initial_capital=1000.0)
    trade = Trade(token="CAKE", action=Action.BUY, price=2.50, size_usd=20.0, is_paper=True)
    p.record_trade(trade)
    assert len(p.trade_history) == 1
