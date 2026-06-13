from __future__ import annotations
from src.config import Config
from src.models import Decision, Action
from src.portfolio import Portfolio


class RiskManager:
    def __init__(self, config: Config):
        self.config = config
        self.force_paper = False

    def check(self, decision: Decision, portfolio: Portfolio) -> tuple[bool, str]:
        if decision.action == Action.HOLD:
            return True, "HOLD — no trade needed"

        # 1. Token allowlist
        if decision.token not in Config.TOKEN_ALLOWLIST:
            return False, f"BLOCKED: {decision.token} not on allowlist"

        # 2. Sufficient cash for BUY
        if decision.action == Action.BUY and portfolio.cash < self.config.max_trade_size:
            return False, f"BLOCKED: insufficient cash ${portfolio.cash:.2f} < ${self.config.max_trade_size}"

        # 3. Drawdown checks (PROTECT logic)
        dd = portfolio.drawdown_pct
        if dd >= self.config.max_drawdown_pct:
            return False, f"BLOCKED: drawdown {dd}% >= {self.config.max_drawdown_pct}% — DQ"

        if 25 <= dd < self.config.max_drawdown_pct:
            self.force_paper = True

        # 4. Sell requires open position
        if decision.action == Action.SELL and decision.token not in portfolio.positions:
            return False, f"BLOCKED: no open position in {decision.token} to sell"

        return True, "OK"
