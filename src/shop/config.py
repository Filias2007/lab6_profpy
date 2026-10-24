import os

def get_min_stock_threshold() -> int:
    try:
        return int(os.getenv("MIN_STOCK_THRESHOLD", "5"))
    except ValueError:
        return 5

def get_payment_gateway_mode() -> str:
    return os.getenv("PAYMENT_GATEWAY_MODE", "sandbox")