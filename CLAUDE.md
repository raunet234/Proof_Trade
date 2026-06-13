# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ProofTrade is a prop-firm-style autonomous crypto trading agent for BSC mainnet. It paper-trades first (Phase 1: June 3-21) then live-trades (Phase 2: June 22-28), controlled by a single config flag. Built for a hackathon with prize tracks for best use of Trust Wallet Agent Kit (TWAK) and CoinMarketCap Agent Hub.

## Architecture

Five-step autonomous loop:

1. **SEE** — CoinMarketCap Agent Hub fetches Fear & Greed Index, price movements (5%+ drops), social sentiment, and runs `portfolio_analysis` skill
2. **THINK** — LLM (Claude or GPT-4) analyzes signals and decides BUY / SELL / HOLD
3. **CHECK** — TWAK enforces guardrails: token on 149-token allowlist, trade size <= $20, portfolio drawdown < 30%
4. **ACT** — TWAK signs transaction locally (keys never leave machine), executes on BSC mainnet
5. **PROTECT** — Prop-firm drawdown logic: <25% = live trading, 25-29% = demote to paper, >=30% = full stop (DQ)

## Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Agent Framework | BNBAgent SDK (`pip install bnbagent`) — ERC-8004 identity + ERC-8183 agentic commerce |
| Market Data | CoinMarketCap AI Agent Hub (MCP tools via `cmc-skill-hub`) |
| Decision Engine | Claude LLM / GPT-4 |
| Risk + Signing | Trust Wallet Agent Kit (TWAK CLI + MCP tools) |
| Blockchain | BSC Mainnet (Chain ID 56) / BSC Testnet (Chain ID 97) |
| Wallet | `EVMWalletProvider` — Keystore V3 encrypted, keys never leave machine |

## BNBAgent SDK

- **ERC-8004**: Register agent identity on-chain, manage wallets, make agent discoverable
- **ERC-8183**: Agentic commerce — negotiate pricing, accept jobs, deliver work, settle payment via on-chain escrow
- Wallet abstraction via `WalletProvider` ABC — `EVMWalletProvider` built-in with keystore encryption
- Storage: `LocalStorageProvider` (default) or `IPFSStorageProvider` for deliverables
- Contracts on BSC Mainnet:
  - Identity Registry: `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`
  - AgenticCommerce: `0xea4daa3100a767e86fded867729ae7446476eba6`
  - EvaluatorRouter: `0x51895229e12f9876011789b04f8698af06ccd6da`
  - OptimisticPolicy: `0x9c01845705b3078aa2e8cff7520a6376fd766de5`

## TWAK (Trust Wallet Agent Kit)

- Installed via `curl -fsSL https://agent-kit.trustwallet.com/install.sh | bash`
- Credentials stored in `~/.twak/` + OS keychain
- Exposes commands as MCP tools for Claude Code
- Non-custodial agent wallet for transaction signing
- Env vars: `TW_ACCESS_ID`, `TW_HMAC_SECRET`

## Trading Strategy

Spot mean reversion on 3-5 liquid tokens (CAKE, BNB, LINK):
- Buy on 5%+ drop with no bad news, Fear & Greed < 30 as signal
- Sell on bounce back to mean
- Hold USDT between trades
- Max 1-2 trades/day

## Key Constraints

- Max $20 per trade (TWAK-enforced)
- 149 eligible tokens only (TWAK allowlist)
- 30% drawdown = disqualification
- Paper/live mode is a config toggle — same codebase for both phases
- Competition contract: `0x212c61b9b72c95d95bf29cf032f5e5635629aed5`

## Key Resources

- CoinMarketCap Agent Hub: https://coinmarketcap.com/api/agent
- Trust Wallet Agent Kit: https://portal.trustwallet.com
- BNBAgent SDK: https://github.com/bnb-chain/bnbagent-sdk
- Full spec: `input.md`
