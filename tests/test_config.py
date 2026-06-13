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
