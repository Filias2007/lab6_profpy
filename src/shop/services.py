from shop.models import Product
from shop.exceptions import InsufficientStockError, PaymentError


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