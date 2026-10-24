import os

def load_config() -> dict:
    env = os.environ.get("SHOP_ENV", "development")
    debug_str = os.environ.get("SHOP_DEBUG", "true").lower()
    debug = debug_str in ("true", "1", "yes")
    return {
        "env": env,
        "debug": debug,
    }