from __future__ import annotations
import json
import subprocess
from src.models import Decision, Action, Trade


class Executor:
    def __init__(self, is_paper: bool):
        self.is_paper = is_paper

    def execute(self, decision: Decision, current_price: float, size_usd: float) -> Trade | None:
        if decision.action == Action.HOLD:
            return None

        if self.is_paper:
            return self._paper_trade(decision, current_price, size_usd)

        return self._live_trade(decision, current_price, size_usd)

    def _paper_trade(self, decision: Decision, price: float, size_usd: float) -> Trade:
        return Trade(
            token=decision.token,
            action=decision.action,
            price=price,
            size_usd=size_usd,
            is_paper=True,
        )

    def _live_trade(self, decision: Decision, price: float, size_usd: float) -> Trade:
        if decision.action == Action.BUY:
            cmd = ["twak", "swap", str(size_usd), "USDT", decision.token, "--chain", "bsc"]
        else:
            quantity = size_usd / price if price > 0 else 0
            cmd = ["twak", "swap", str(quantity), decision.token, "USDT", "--chain", "bsc"]

        result = subprocess.run(cmd, capture_output=True, text=True)

        tx_hash = None
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                tx_hash = data.get("txHash")
            except json.JSONDecodeError:
                pass

        return Trade(
            token=decision.token,
            action=decision.action,
            price=price,
            size_usd=size_usd,
            is_paper=False,
            tx_hash=tx_hash,
        )
