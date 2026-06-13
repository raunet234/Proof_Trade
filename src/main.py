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

LOOP_INTERVAL_SECONDS = 3600


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
