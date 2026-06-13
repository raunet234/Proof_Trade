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

    TOKEN_ALLOWLIST: set[str] = None  # class-level, set below

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
