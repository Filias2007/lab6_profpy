from shop.models import Catalog, Product
from shop.exceptions import PaymentError, InsufficientStockError

class DiscountService:
    def apply_percentage_discount(self, product: Product, percent: float) -> float:
        if not (0 <= percent <= 100):
            raise ValueError("Discount percent must be between 0 and 100")
        return round(product.price.amount * (1 - percent / 100.0), 2)

class OrderService:
    def __init__(self, payment_gateway, notifier) -> None:
        self.gateway = payment_gateway
        self.notifier = notifier

    def checkout(self, customer_email: str, product: Product, quantity: int) -> str:
        if product.quantity < quantity:
            raise InsufficientStockError(f"Not enough stock for {product.name}")
        
        total_price = product.price.amount * quantity
        payment_id = self.gateway.pay(total_price)
        if not payment_id:
            raise PaymentError("Payment processing failed")
        
        self.notifier.send_notification(customer_email, f"Order confirmed: {payment_id}")
        product.quantity -= quantity
        return payment_id

class AsyncSupplierService:
    def __init__(self, async_provider) -> None:
        self.provider = async_provider

    async def fetch_external_stock(self, product_id: int) -> int:
        data = await self.provider.get_stock_info(product_id)
        return data.get("available_stock", 0)