import os

DEFAULT_MIN_STOCK = 5


def load_config() -> dict:
    env = os.environ.get("SHOP_ENV", "development")
    debug_str = os.environ.get("SHOP_DEBUG", "true").lower()
    debug = debug_str in ("true", "1", "yes")

    min_stock_str = os.environ.get("SHOP_MIN_STOCK", str(DEFAULT_MIN_STOCK))
    try:
        min_stock = int(min_stock_str)
    except ValueError as err:
        raise ValueError(
            f"SHOP_MIN_STOCK must be an integer, got: {min_stock_str!r}"
        ) from err
    if min_stock < 0:
        raise ValueError("SHOP_MIN_STOCK cannot be negative")

    return {
        "env": env,
        "debug": debug,
        "min_stock": min_stock,
    }