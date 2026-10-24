import pytest
from shop.config import load_app_config


@pytest.mark.integration
def test_config_from_monkeypatch(monkeypatch):
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.setenv("MIN_STOCK_THRESHOLD", "20")

    cfg = load_app_config()
    assert cfg["env"] == "testing"
    assert cfg["min_stock_threshold"] == 20


@pytest.mark.integration
def test_config_defaults(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("MIN_STOCK_THRESHOLD", raising=False)

    cfg = load_app_config()
    assert cfg["env"] == "development"
    assert cfg["min_stock_threshold"] == 5