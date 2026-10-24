import os


def load_app_config() -> dict:
    env = os.getenv("APP_ENV", "development")
    min_stock = int(os.getenv("MIN_STOCK_THRESHOLD", "5"))
    return {
        "env": env,
        "min_stock_threshold": min_stock,
    }