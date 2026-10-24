import pytest

from shop.config import DEFAULT_MIN_STOCK, load_config


def test_load_config_env_vars(monkeypatch):
    monkeypatch.setenv("SHOP_ENV", "production")
    monkeypatch.setenv("SHOP_DEBUG", "false")
    monkeypatch.setenv("SHOP_MIN_STOCK", "12")

    cfg = load_config()
    assert cfg["env"] == "production"
    assert cfg["debug"] is False
    assert cfg["min_stock"] == 12


def test_load_config_defaults(monkeypatch):
    for name in ("SHOP_ENV", "SHOP_DEBUG", "SHOP_MIN_STOCK"):
        monkeypatch.delenv(name, raising=False)

    cfg = load_config()
    assert cfg["env"] == "development"
    assert cfg["debug"] is True
    assert cfg["min_stock"] == DEFAULT_MIN_STOCK


@pytest.mark.parametrize(
    "raw, expected",
    [("true", True), ("TRUE", True), ("1", True), ("yes", True),
     ("false", False), ("0", False), ("no", False), ("", False)],
)
def test_debug_flag_parsing(monkeypatch, raw, expected):
    monkeypatch.setenv("SHOP_DEBUG", raw)
    assert load_config()["debug"] is expected


def test_min_stock_zero_is_valid_boundary(monkeypatch):
    monkeypatch.setenv("SHOP_MIN_STOCK", "0")
    assert load_config()["min_stock"] == 0


def test_min_stock_negative_raises(monkeypatch):
    monkeypatch.setenv("SHOP_MIN_STOCK", "-1")
    with pytest.raises(ValueError, match="cannot be negative"):
        load_config()


def test_min_stock_not_integer_raises_with_chaining(monkeypatch):
    monkeypatch.setenv("SHOP_MIN_STOCK", "many")
    with pytest.raises(ValueError, match="must be an integer") as exc_info:
        load_config()
    assert isinstance(exc_info.value.__cause__, ValueError)