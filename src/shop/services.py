from typing import Protocol
from shop.models import Product, Cart, Money, InsufficientStockError


class PaymentGateway(Protocol):
    def pay(self, amount: float) -> str:
        ...


class Notifier(Protocol):
    def send_notification(self, recipient: str, message: str) -> None:
        ...


class PercentageDiscount:
    def __init__(self, percent: float) -> None:
        if not (0 <= percent <= 100):
            raise ValueError("Invalid discount percentage")
        self.percent = percent

    def apply(self, total: Money) -> Money:
        return Money(
            round(total.amount * (1 - self.percent / 100), 2),
            total.currency,
        )


class CheckoutService:
    def __init__(self, payment_gateway: PaymentGateway, notifier: Notifier) -> None:
        self.payment_gateway = payment_gateway
        self.notifier = notifier

    def checkout(self, email: str, cart: Cart) -> str:
        if len(cart) == 0:
            raise ValueError("Cart is empty")

        total_amount = cart.total.amount
        payment_id = self.payment_gateway.pay(total_amount)
        self.notifier.send_notification(email, f"Payment successful: {payment_id}")
        return payment_id


class AsyncSupplierService:
    def __init__(self, provider_client) -> None:
        self.provider_client = provider_client

    async def fetch_external_stock(self, product_id: int) -> int:
        data = await self.provider_client.get_stock_info(product_id)
        return data.get("available_stock", 0)