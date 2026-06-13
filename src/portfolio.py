from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass, field

from src.models import Action, Trade, Position


@dataclass
class Portfolio:
    initial_capital: float
    cash: float = 0.0
    positions: dict[str, Position] = field(default_factory=dict)
    trade_history: list[Trade] = field(default_factory=list)
    peak_value: float = 0.0

    def __post_init__(self):
        if self.cash == 0.0:
            self.cash = self.initial_capital
        if self.peak_value == 0.0:
            self.peak_value = self.initial_capital

    @property
    def total_value(self) -> float:
        position_value = sum(p.size_usd for p in self.positions.values())
        return self.cash + position_value

    @property
    def drawdown_pct(self) -> float:
        if self.peak_value == 0:
            return 0.0
        current = self.total_value
        return round((1 - current / self.peak_value) * 100, 2)

    def update_peak(self) -> None:
        current = self.total_value
        if current > self.peak_value:
            self.peak_value = current

    def record_trade(self, trade: Trade) -> None:
        if trade.action == Action.BUY:
            quantity = trade.size_usd / trade.price
            self.cash -= trade.size_usd
            self.positions[trade.token] = Position(
                token=trade.token,
                entry_price=trade.price,
                size_usd=trade.size_usd,
                quantity=quantity,
            )
        elif trade.action == Action.SELL:
            if trade.token in self.positions:
                pos = self.positions.pop(trade.token)
                sell_value = pos.quantity * trade.price
                self.cash += sell_value
                trade.pnl = sell_value - pos.size_usd

        self.trade_history.append(trade)
        self.update_peak()

    def save(self, path: str = "data/trades.json") -> None:
        filepath = Path(path)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        records = []
        for t in self.trade_history:
            records.append({
                "token": t.token,
                "action": t.action.value,
                "price": t.price,
                "size_usd": t.size_usd,
                "is_paper": t.is_paper,
                "timestamp": t.timestamp.isoformat(),
                "tx_hash": t.tx_hash,
                "pnl": t.pnl,
            })
        filepath.write_text(json.dumps(records, indent=2))

    @classmethod
    def load(cls, initial_capital: float, path: str = "data/trades.json") -> Portfolio:
        filepath = Path(path)
        portfolio = cls(initial_capital=initial_capital)
        if filepath.exists():
            records = json.loads(filepath.read_text())
            for r in records:
                trade = Trade(
                    token=r["token"],
                    action=Action(r["action"]),
                    price=r["price"],
                    size_usd=r["size_usd"],
                    is_paper=r["is_paper"],
                )
                portfolio.record_trade(trade)
        return portfolio
