# ProofTrade

Prop-firm-style autonomous crypto trading agent on BSC mainnet. Paper-trades first, then live-trades — controlled by a single config flag.

Built for the BNB Chain hackathon with prize tracks for best use of **Trust Wallet Agent Kit (TWAK)** and **CoinMarketCap Agent Hub**.

## How It Works

Five-step autonomous loop:

```
SEE → THINK → CHECK → ACT → PROTECT
```

1. **SEE** — Fetches Fear & Greed Index, price movements, and sentiment via CoinMarketCap API
2. **THINK** — Claude LLM analyzes signals and decides BUY / SELL / HOLD
3. **CHECK** — Risk manager enforces guardrails: token allowlist, trade size ($20 max), drawdown limits
4. **ACT** — Executes trade (paper or live via TWAK on BSC)
5. **PROTECT** — Prop-firm drawdown logic: <25% live, 25-29% demote to paper, >=30% full stop (DQ)

## Trading Strategy

Spot mean reversion on liquid BSC tokens (CAKE, BNB, LINK):

- Buy on 5%+ drop with Fear & Greed < 30
- Sell on bounce back to mean
- Hold USDT between trades
- Max 1-2 trades/day

## Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Agent Identity | BNBAgent SDK (ERC-8004) |
| Market Data | CoinMarketCap API |
| Decision Engine | Claude API |
| Trade Execution | Trust Wallet Agent Kit (TWAK CLI) |
| Blockchain | BSC Mainnet (Chain ID 56) |

## Setup

```bash
# Clone and create virtualenv
python3.11 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Required Environment Variables

```
TRADING_MODE=paper          # paper or live
CMC_API_KEY=                # CoinMarketCap API key
ANTHROPIC_API_KEY=          # Claude API key
TW_ACCESS_ID=               # Trust Wallet Agent Kit access ID
TW_HMAC_SECRET=             # Trust Wallet HMAC secret
WALLET_PASSWORD=            # Agent wallet password
PRIVATE_KEY=                # Wallet private key
INITIAL_CAPITAL=1000        # Starting capital in USD
MAX_TRADE_SIZE=20           # Max per-trade size in USD
MAX_DRAWDOWN_PCT=30         # Drawdown threshold for DQ
TARGET_TOKENS=CAKE,BNB,LINK # Comma-separated token list
```

## Run

```bash
# Start the trading agent
python -m src.main
```

## Test

```bash
pytest tests/ -v
```

33 tests across 8 modules.

## Project Structure

```
src/
  models.py          # Signal, Decision, Trade, Position dataclasses
  config.py          # Environment config with paper/live toggle
  market_data.py     # CMC API client (SEE)
  decision_engine.py # Claude LLM decisions (THINK)
  risk_manager.py    # Guardrails and allowlist (CHECK)
  executor.py        # Paper + TWAK live trades (ACT)
  portfolio.py       # Cash, positions, drawdown tracking (PROTECT)
  agent_identity.py  # ERC-8004 on-chain registration
  main.py            # Orchestration loop
tests/               # Unit tests for all modules
data/                # Trade logs (JSON)
```

## Key Constraints

- Max $20 per trade (TWAK-enforced)
- 16 eligible tokens from TWAK allowlist
- 30% drawdown = disqualification
- Paper/live mode is a config toggle — same codebase for both phases

## License

MIT
