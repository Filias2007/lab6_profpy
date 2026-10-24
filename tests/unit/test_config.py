import pytest
from shop.config import load_config

def test_load_config_env_vars(monkeypatch):
    monkeypatch.setenv("SHOP_ENV", "production")
    monkeypatch.setenv("SHOP_DEBUG", "false")

    cfg = load_config()
    assert cfg["env"] == "production"
    assert cfg["debug"] is False

def test_load_config_defaults(monkeypatch):
    monkeypatch.delenv("SHOP_ENV", raising=False)
    monkeypatch.delenv("SHOP_DEBUG", raising=False)

    cfg = load_config()
    assert cfg["env"] == "development"
    assert cfg["debug"] is True