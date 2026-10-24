class ShopException(Exception):
    """Базовий виняток предметної області Інтернет-магазину."""
    pass

class ProductValidationError(ShopException):
    """Помилка валідації полів товару."""
    pass

class InsufficientStockError(ShopException):
    """Помилка недостатньої кількості товару на складі."""
    pass

class PaymentError(ShopException):
    """Помилка під час проведення платежу."""
    pass