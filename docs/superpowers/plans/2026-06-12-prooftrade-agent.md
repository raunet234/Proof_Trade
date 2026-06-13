# ProofTrade Autonomous Trading Agent — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a prop-firm-style autonomous crypto trading agent on BSC that paper-trades and live-trades using a 5-step loop (SEE → THINK → CHECK → ACT → PROTECT).

**Architecture:** Python application with a main trading loop that: (1) fetches market data via CMC API, (2) sends signals to Claude for BUY/SELL/HOLD decisions, (3) validates against risk guardrails, (4) executes trades via TWAK CLI on BSC, (5) enforces drawdown protection. Config toggle switches between paper and live mode. BNBAgent SDK registers the agent's on-chain identity via ERC-8004.

**Tech Stack:** Python 3.10+, BNBAgent SDK (`bnbagent`), TWAK CLI, CoinMarketCap API, Anthropic Claude API, BSC Mainnet (Chain 56)

---

## File Structure

```
Proof_Trade/
├── pyproject.toml              # Project config, dependencies
├── .env.example                # Template for env vars
├── .gitignore                  # Python + env ignores
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point — runs the trading loop
│   ├── config.py               # Config loading, paper/live toggle
│   ├── market_data.py          # SEE — CMC API for prices, fear & greed, sentiment
│   ├── decision_engine.py      # THINK — Claude LLM for BUY/SELL/HOLD
│   ├── risk_manager.py         # CHECK — guardrails (allowlist, max size, drawdown)
│   ├── executor.py             # ACT — TWAK CLI wrapper for BSC transactions
│   ├── portfolio.py            # Portfolio state, P&L tracking, drawdown calc
│   ├── agent_identity.py       # ERC-8004 on-chain registration via BNBAgent SDK
│   └── models.py               # Data classes: Signal, Decision, Trade, Position
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_market_data.py
│   ├── test_decision_engine.py
│   ├── test_risk_manager.py
│   ├── test_executor.py
│   ├── test_portfolio.py
│   └── test_models.py
└── data/
    └── trades.json             # Local trade log (created at runtime)
```

---

### Task 1: Project Skeleton & Dependencies

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `src/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "prooftrade"
version = "0.1.0"
description = "Prop-firm-style autonomous crypto trading agent on BSC"
requires-python = ">=3.10"
dependencies = [
    "bnbagent",
    "anthropic",
    "httpx",
    "python-dotenv",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio",
    "pytest-mock",
]

[project.scripts]
prooftrade = "src.main:main"
```

- [ ] **Step 2: Create `.env.example`**

```bash
# Mode: "paper" or "live"
TRADING_MODE=paper

# CoinMarketCap API
CMC_API_KEY=your-cmc-api-key

# Anthropic Claude
ANTHROPIC_API_KEY=your-anthropic-api-key

# Trust Wallet Agent Kit
TW_ACCESS_ID=your-tw-access-id
TW_HMAC_SECRET=your-tw-hmac-secret

# BNBAgent SDK
WALLET_PASSWORD=your-wallet-password
PRIVATE_KEY=0x...

# Trading params
INITIAL_CAPITAL=1000
MAX_TRADE_SIZE=20
MAX_DRAWDOWN_PCT=30
```

- [ ] **Step 3: Create `.gitignore`**

```
__pycache__/
*.pyc
.env
.venv/
venv/
dist/
*.egg-info/
data/trades.json
.agent-data/
~/.bnbagent/
.pytest_cache/
```

- [ ] **Step 4: Create empty `src/__init__.py` and `tests/__init__.py`**

Both files are empty — just mark the directories as Python packages.

- [ ] **Step 5: Install dependencies**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

Expected: all deps install successfully, `bnbagent`, `anthropic`, `httpx`, `pydantic` available.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml .env.example .gitignore src/__init__.py tests/__init__.py
git commit -m "feat: project skeleton with dependencies"
```

---

### Task 2: Data Models

**Files:**
- Create: `src/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.models'`

- [ ] **Step 3: Write the implementation**

```python
# src/models.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models.py -v`
Expected: all 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/models.py tests/test_models.py
git commit -m "feat: data models for Signal, Decision, Trade, Position"
```

---

### Task 3: Config Module

**Files:**
- Create: `src/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_config.py
import os
from src.config import Config

def test_config_defaults(monkeypatch):
    monkeypatch.setenv("CMC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    config = Config.from_env()
    assert config.trading_mode == "paper"
    assert config.max_trade_size == 20.0
    assert config.max_drawdown_pct == 30.0
    assert config.initial_capital == 1000.0

def test_config_live_mode(monkeypatch):
    monkeypatch.setenv("TRADING_MODE", "live")
    monkeypatch.setenv("CMC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    config = Config.from_env()
    assert config.trading_mode == "live"
    assert config.is_paper is False

def test_config_paper_mode(monkeypatch):
    monkeypatch.setenv("TRADING_MODE", "paper")
    monkeypatch.setenv("CMC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    config = Config.from_env()
    assert config.is_paper is True

def test_config_allowlist():
    config = Config.from_env.__wrapped__ if hasattr(Config.from_env, '__wrapped__') else None
    # Test the allowlist contains our target tokens
    assert "CAKE" in Config.TOKEN_ALLOWLIST
    assert "BNB" in Config.TOKEN_ALLOWLIST
    assert "LINK" in Config.TOKEN_ALLOWLIST

def test_config_missing_api_key(monkeypatch):
    monkeypatch.delenv("CMC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    try:
        Config.from_env()
        assert False, "Should have raised"
    except ValueError:
        pass
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write the implementation**

```python
# src/config.py
from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Config:
    trading_mode: str
    cmc_api_key: str
    anthropic_api_key: str
    tw_access_id: str
    tw_hmac_secret: str
    wallet_password: str
    private_key: str
    initial_capital: float
    max_trade_size: float
    max_drawdown_pct: float
    target_tokens: list[str]

    TOKEN_ALLOWLIST: set[str] = None  # class-level, set in __init_subclass__ or below

    @property
    def is_paper(self) -> bool:
        return self.trading_mode == "paper"

    @classmethod
    def from_env(cls) -> Config:
        load_dotenv()

        cmc_key = os.getenv("CMC_API_KEY", "")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

        if not cmc_key or not anthropic_key:
            raise ValueError("CMC_API_KEY and ANTHROPIC_API_KEY are required")

        return cls(
            trading_mode=os.getenv("TRADING_MODE", "paper"),
            cmc_api_key=cmc_key,
            anthropic_api_key=anthropic_key,
            tw_access_id=os.getenv("TW_ACCESS_ID", ""),
            tw_hmac_secret=os.getenv("TW_HMAC_SECRET", ""),
            wallet_password=os.getenv("WALLET_PASSWORD", ""),
            private_key=os.getenv("PRIVATE_KEY", ""),
            initial_capital=float(os.getenv("INITIAL_CAPITAL", "1000")),
            max_trade_size=float(os.getenv("MAX_TRADE_SIZE", "20")),
            max_drawdown_pct=float(os.getenv("MAX_DRAWDOWN_PCT", "30")),
            target_tokens=os.getenv("TARGET_TOKENS", "CAKE,BNB,LINK").split(","),
        )


# Primary trading tokens — subset of the 149 TWAK-approved tokens
Config.TOKEN_ALLOWLIST = {
    "CAKE", "BNB", "LINK", "ETH", "BTCB", "USDT", "USDC", "XRP",
    "ADA", "DOT", "AVAX", "MATIC", "UNI", "AAVE", "DOGE", "SOL",
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: all 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: config module with paper/live toggle and env loading"
```

---

### Task 4: Portfolio Tracker

**Files:**
- Create: `src/portfolio.py`
- Create: `tests/test_portfolio.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_portfolio.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_portfolio.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write the implementation**

```python
# src/portfolio.py
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
        # For accurate valuation, positions need current prices.
        # This returns cash + cost basis of open positions as a floor.
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_portfolio.py -v`
Expected: all 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/portfolio.py tests/test_portfolio.py
git commit -m "feat: portfolio tracker with P&L, drawdown, and persistence"
```

---

### Task 5: Risk Manager (CHECK)

**Files:**
- Create: `src/risk_manager.py`
- Create: `tests/test_risk_manager.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_risk_manager.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_risk_manager.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write the implementation**

```python
# src/risk_manager.py
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

        # 2. Drawdown checks (PROTECT logic)
        dd = portfolio.drawdown_pct
        if dd >= self.config.max_drawdown_pct:
            return False, f"BLOCKED: drawdown {dd}% >= {self.config.max_drawdown_pct}% — DQ"

        if 25 <= dd < self.config.max_drawdown_pct:
            self.force_paper = True

        # 3. Sufficient cash for BUY
        if decision.action == Action.BUY and portfolio.cash < self.config.max_trade_size:
            return False, f"BLOCKED: insufficient cash ${portfolio.cash:.2f} < ${self.config.max_trade_size}"

        # 4. Sell requires open position
        if decision.action == Action.SELL and decision.token not in portfolio.positions:
            return False, f"BLOCKED: no open position in {decision.token} to sell"

        return True, "OK"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_risk_manager.py -v`
Expected: all 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/risk_manager.py tests/test_risk_manager.py
git commit -m "feat: risk manager with allowlist, drawdown, and cash checks"
```

---

### Task 6: Market Data Module (SEE)

**Files:**
- Create: `src/market_data.py`
- Create: `tests/test_market_data.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_market_data.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_market_data.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write the implementation**

```python
# src/market_data.py
from __future__ import annotations
import httpx
from src.models import Signal

CMC_BASE = "https://pro-api.coinmarketcap.com"


class MarketDataClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "X-CMC_PRO_API_KEY": api_key,
            "Accept": "application/json",
        }

    async def fetch_fear_greed(self) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{CMC_BASE}/v3/fear-and-greed/latest",
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()["data"]

    async def fetch_price(self, symbol: str) -> tuple[float, float]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{CMC_BASE}/v2/cryptocurrency/quotes/latest",
                headers=self.headers,
                params={"symbol": symbol, "convert": "USD"},
            )
            resp.raise_for_status()
            data = resp.json()["data"][symbol]
            # CMC returns a list for symbols; take first entry
            if isinstance(data, list):
                data = data[0]
            quote = data["quote"]["USD"]
            return quote["price"], quote["percent_change_24h"]

    async def build_signal(self, token: str) -> Signal:
        fg = await self.fetch_fear_greed()
        price, change = await self.fetch_price(token)
        return Signal(
            fear_greed_index=fg["value"],
            price_change_pct=change,
            token=token,
            current_price=price,
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_market_data.py -v`
Expected: all 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/market_data.py tests/test_market_data.py
git commit -m "feat: market data client with CMC API for prices and fear/greed"
```

---

### Task 7: Decision Engine (THINK)

**Files:**
- Create: `src/decision_engine.py`
- Create: `tests/test_decision_engine.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_decision_engine.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_decision_engine.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write the implementation**

```python
# src/decision_engine.py
from __future__ import annotations
import json
import anthropic
from src.models import Signal, Decision, Action

SYSTEM_PROMPT = """You are a crypto trading analyst for a prop-firm-style agent on BSC.

Strategy: Spot mean reversion on liquid tokens.
- BUY when: 5%+ price drop AND Fear & Greed < 30 AND no bad news
- SELL when: price bounces back to mean (recovers most of the drop)
- HOLD otherwise

Rules:
- Max 1-2 trades per day
- Conservative — when in doubt, HOLD
- Never chase pumps

Respond with ONLY a JSON object:
{"action": "BUY" | "SELL" | "HOLD", "reason": "short explanation", "confidence": 0.0-1.0}
"""


class DecisionEngine:
    def __init__(self, api_key: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def decide(self, signal: Signal) -> Decision:
        prompt = (
            f"Token: {signal.token}\n"
            f"Current price: ${signal.current_price:.4f}\n"
            f"24h change: {signal.price_change_pct:+.2f}%\n"
            f"Fear & Greed Index: {signal.fear_greed_index}/100\n"
            f"Sentiment: {signal.sentiment}\n\n"
            f"What is your decision?"
        )

        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=200,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text
            data = json.loads(raw)
            return Decision(
                action=Action(data["action"]),
                token=signal.token,
                reason=data["reason"],
                confidence=data["confidence"],
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return Decision(
                action=Action.HOLD,
                token=signal.token,
                reason="Failed to parse LLM response — defaulting to HOLD",
                confidence=0.0,
            )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_decision_engine.py -v`
Expected: all 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/decision_engine.py tests/test_decision_engine.py
git commit -m "feat: decision engine using Claude for BUY/SELL/HOLD signals"
```

---

### Task 8: Executor (ACT)

**Files:**
- Create: `src/executor.py`
- Create: `tests/test_executor.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_executor.py
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
        mock_run.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_executor.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write the implementation**

```python
# src/executor.py
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
        side = "buy" if decision.action == Action.BUY else "sell"
        result = subprocess.run(
            [
                "twak", "swap",
                "--token", decision.token,
                "--side", side,
                "--amount", str(size_usd),
                "--chain", "bsc",
            ],
            capture_output=True,
            text=True,
        )

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_executor.py -v`
Expected: all 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/executor.py tests/test_executor.py
git commit -m "feat: executor with paper trading and TWAK live trading"
```

---

### Task 9: Agent Identity (ERC-8004)

**Files:**
- Create: `src/agent_identity.py`
- Create: `tests/test_agent_identity.py`  (placeholder — requires network)

- [ ] **Step 1: Write the test (mock-based, no network)**

```python
# tests/test_agent_identity.py
from unittest.mock import patch, MagicMock
from src.agent_identity import register_agent

def test_register_agent_calls_sdk():
    mock_sdk = MagicMock()
    mock_sdk.generate_agent_uri.return_value = "uri://test"
    mock_sdk.register_agent.return_value = {"agentId": 42, "transactionHash": "0xabc"}

    with patch("src.agent_identity.ERC8004Agent", return_value=mock_sdk):
        with patch("src.agent_identity.EVMWalletProvider"):
            result = register_agent(
                wallet_password="test",
                private_key="0x123",
                network="bsc-testnet",
            )
            assert result["agentId"] == 42
            mock_sdk.register_agent.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_agent_identity.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write the implementation**

```python
# src/agent_identity.py
from __future__ import annotations
from bnbagent import ERC8004Agent, AgentEndpoint, EVMWalletProvider


def register_agent(
    wallet_password: str,
    private_key: str,
    network: str = "bsc-testnet",
    name: str = "ProofTrade",
    description: str = "Prop-firm-style autonomous crypto trading agent on BSC",
) -> dict:
    wallet = EVMWalletProvider(
        password=wallet_password,
        private_key=private_key,
    )

    sdk = ERC8004Agent(network=network, wallet_provider=wallet)

    agent_uri = sdk.generate_agent_uri(
        name=name,
        description=description,
        endpoints=[
            AgentEndpoint(
                name="ProofTrade-Agent",
                endpoint="https://prooftrade.example.com/status",
                version="0.1.0",
            ),
        ],
    )

    result = sdk.register_agent(agent_uri=agent_uri)
    return result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_agent_identity.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/agent_identity.py tests/test_agent_identity.py
git commit -m "feat: ERC-8004 agent identity registration via BNBAgent SDK"
```

---

### Task 10: Main Loop — Orchestration

**Files:**
- Create: `src/main.py`

- [ ] **Step 1: Write the main loop**

```python
# src/main.py
from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timezone

from src.config import Config
from src.market_data import MarketDataClient
from src.decision_engine import DecisionEngine
from src.risk_manager import RiskManager
from src.executor import Executor
from src.portfolio import Portfolio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("prooftrade")

LOOP_INTERVAL_SECONDS = 3600  # 1 hour between scans


async def run_cycle(
    config: Config,
    market: MarketDataClient,
    engine: DecisionEngine,
    risk: RiskManager,
    executor: Executor,
    portfolio: Portfolio,
) -> None:
    for token in config.target_tokens:
        log.info(f"--- Scanning {token} ---")

        # 1. SEE
        try:
            signal = await market.build_signal(token)
            log.info(f"Signal: F&G={signal.fear_greed_index}, price=${signal.current_price:.4f}, 24h={signal.price_change_pct:+.2f}%")
        except Exception as e:
            log.error(f"SEE failed for {token}: {e}")
            continue

        # 2. THINK
        try:
            decision = await engine.decide(signal)
            log.info(f"Decision: {decision.action.value} — {decision.reason} (conf={decision.confidence:.2f})")
        except Exception as e:
            log.error(f"THINK failed for {token}: {e}")
            continue

        # 3. CHECK
        ok, reason = risk.check(decision, portfolio)
        if not ok:
            log.warning(f"CHECK blocked: {reason}")
            continue
        log.info(f"CHECK passed: {reason}")

        # 4. ACT
        is_paper = config.is_paper or risk.force_paper
        executor_instance = Executor(is_paper=is_paper)
        trade = executor_instance.execute(
            decision,
            current_price=signal.current_price,
            size_usd=config.max_trade_size,
        )

        if trade:
            portfolio.record_trade(trade)
            mode = "PAPER" if trade.is_paper else "LIVE"
            log.info(f"ACT [{mode}]: {trade.action.value} {trade.token} @ ${trade.price:.4f} (${trade.size_usd})")

        # 5. PROTECT
        dd = portfolio.drawdown_pct
        log.info(f"PROTECT: drawdown={dd:.2f}%, cash=${portfolio.cash:.2f}, peak=${portfolio.peak_value:.2f}")

        if dd >= config.max_drawdown_pct:
            log.critical(f"DRAWDOWN {dd}% >= {config.max_drawdown_pct}% — FULL STOP (DQ)")
            portfolio.save()
            return

    portfolio.save()
    log.info(f"Cycle complete. Portfolio: cash=${portfolio.cash:.2f}, positions={list(portfolio.positions.keys())}")


async def run_loop(config: Config) -> None:
    market = MarketDataClient(api_key=config.cmc_api_key)
    engine = DecisionEngine(api_key=config.anthropic_api_key)
    risk = RiskManager(config)
    executor = Executor(is_paper=config.is_paper)
    portfolio = Portfolio.load(initial_capital=config.initial_capital)

    log.info(f"ProofTrade starting — mode={'PAPER' if config.is_paper else 'LIVE'}, capital=${config.initial_capital}")
    log.info(f"Tokens: {config.target_tokens}")

    while True:
        await run_cycle(config, market, engine, risk, executor, portfolio)
        log.info(f"Sleeping {LOOP_INTERVAL_SECONDS}s until next cycle...")
        await asyncio.sleep(LOOP_INTERVAL_SECONDS)


def main():
    config = Config.from_env()
    asyncio.run(run_loop(config))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke test — verify it starts in paper mode**

Create a `.env` file with test values and run:

```bash
cp .env.example .env
# Fill in real CMC_API_KEY and ANTHROPIC_API_KEY
python -m src.main
```

Expected: Logs show "ProofTrade starting — mode=PAPER", scans tokens, makes decisions, records paper trades.

- [ ] **Step 3: Commit**

```bash
git add src/main.py
git commit -m "feat: main trading loop orchestrating SEE/THINK/CHECK/ACT/PROTECT"
```

---

### Task 11: Create `data/` directory and final wiring

**Files:**
- Create: `data/.gitkeep`

- [ ] **Step 1: Create data directory**

```bash
mkdir -p data
touch data/.gitkeep
```

- [ ] **Step 2: Verify full test suite passes**

```bash
pytest tests/ -v
```

Expected: All tests pass (models, config, portfolio, risk_manager, market_data, decision_engine, executor, agent_identity).

- [ ] **Step 3: Commit**

```bash
git add data/.gitkeep
git commit -m "feat: data directory for trade logs"
```

---

## Summary

| Task | Module | What it does |
|------|--------|-------------|
| 1 | Skeleton | pyproject.toml, .env, .gitignore, venv |
| 2 | Models | Signal, Decision, Trade, Position dataclasses |
| 3 | Config | Env loading, paper/live toggle, token allowlist |
| 4 | Portfolio | Cash tracking, P&L, drawdown calc, persistence |
| 5 | Risk Manager | CHECK — allowlist, drawdown, cash guardrails |
| 6 | Market Data | SEE — CMC API for fear/greed + prices |
| 7 | Decision Engine | THINK — Claude LLM for BUY/SELL/HOLD |
| 8 | Executor | ACT — paper trades + TWAK live trades |
| 9 | Agent Identity | ERC-8004 on-chain registration |
| 10 | Main Loop | Orchestrates the full 5-step cycle |
| 11 | Final wiring | Data dir, full test suite verification |
