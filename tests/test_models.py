from src.models import Signal, Decision, Trade, Position, Action

def test_signal_creation():
    signal = Signal(
        fear_greed_index=18,
        price_change_pct=-6.2,
        token="CAKE",
        current_price=2.45,
    )
    assert signal.fear_greed_index == 18
    assert signal.token == "CAKE"

def test_decision_creation():
    decision = Decision(
        action=Action.BUY,
        token="CAKE",
        reason="5%+ drop with extreme fear",
        confidence=0.8,
    )
    assert decision.action == Action.BUY

def test_trade_creation():
    trade = Trade(
        token="CAKE",
        action=Action.BUY,
        price=2.45,
        size_usd=20.0,
        is_paper=True,
    )
    assert trade.is_paper is True
    assert trade.pnl is None

def test_position_pnl():
    pos = Position(
        token="CAKE",
        entry_price=2.45,
        size_usd=20.0,
        quantity=8.163,
    )
    pnl = pos.unrealized_pnl(current_price=2.70)
    assert pnl > 0

def test_position_pnl_loss():
    pos = Position(
        token="CAKE",
        entry_price=2.45,
        size_usd=20.0,
        quantity=8.163,
    )
    pnl = pos.unrealized_pnl(current_price=2.20)
    assert pnl < 0
