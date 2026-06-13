from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Action(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class Signal:
    fear_greed_index: int
    price_change_pct: float
    token: str
    current_price: float
    sentiment: str = "neutral"


@dataclass
class Decision:
    action: Action
    token: str
    reason: str
    confidence: float


@dataclass
class Trade:
    token: str
    action: Action
    price: float
    size_usd: float
    is_paper: bool
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tx_hash: str | None = None
    pnl: float | None = None


@dataclass
class Position:
    token: str
    entry_price: float
    size_usd: float
    quantity: float

    def unrealized_pnl(self, current_price: float) -> float:
        return self.quantity * (current_price - self.entry_price)
