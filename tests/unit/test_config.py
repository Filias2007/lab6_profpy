from shop.config import get_min_stock_threshold, get_payment_gateway_mode

def test_config_min_stock_monkeypatch(monkeypatch):
    monkeypatch.setenv("MIN_STOCK_THRESHOLD", "15")
    assert get_min_stock_threshold() == 15

def test_config_min_stock_default(monkeypatch):
    monkeypatch.delenv("MIN_STOCK_THRESHOLD", raising=False)
    assert get_min_stock_threshold() == 5

def test_config_payment_mode_monkeypatch(monkeypatch):
    monkeypatch.setenv("PAYMENT_GATEWAY_MODE", "production")
    assert get_payment_gateway_mode() == "production"