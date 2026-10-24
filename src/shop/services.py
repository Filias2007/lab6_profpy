from shop.models import Product
from shop.config import load_config
from shop.exceptions import InsufficientStockError


class DiscountService:
    def apply_percentage_discount(self, product: Product, percentage: float) -> float:
        if not (0 <= percentage <= 100):
            raise ValueError("Discount percentage must be between 0 and 100")
        discount_amount = product.price.amount * (percentage / 100.0)
        return round(product.price.amount - discount_amount, 2)


class OrderService:
    def __init__(self, payment_gateway, notifier) -> None:
        self.payment_gateway = payment_gateway
        self.notifier = notifier

    def checkout(self, customer_email: str, product: Product, quantity: int) -> str:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if product.quantity < quantity:
            raise InsufficientStockError("Not enough stock available")

        total_price = product.price.amount * quantity
        payment_id = self.payment_gateway.pay(total_price)

        product.quantity -= quantity
        self.notifier.send_notification(
            customer_email, f"Order confirmed: {payment_id}"
        )

        return payment_id


class AsyncSupplierService:
    def __init__(self, supplier_provider) -> None:
        self.supplier_provider = supplier_provider

    async def fetch_external_stock(self, product_id: int) -> int:
        stock_info = await self.supplier_provider.get_stock_info(product_id)
        return stock_info.get("available_stock", 0)

class InventoryReportService:
    def __init__(self, repository, notifier, min_stock: int | None = None) -> None:
        self.repository = repository
        self.notifier = notifier
        self.min_stock = load_config()["min_stock"] if min_stock is None else min_stock

    def find_low_stock_names(self) -> list[str]:
        return [
            p.name for p in self.repository.get_all() if p.quantity < self.min_stock
        ]

    def notify_low_stock(self, manager_email: str) -> int:
        names = self.find_low_stock_names()
        if not names:
            return 0
        self.notifier.send_notification(
            manager_email, "Low stock: " + ", ".join(names)
        )
        return len(names)