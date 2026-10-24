from typing import Protocol


class PaymentGateway(Protocol):
    def pay(self, amount: float) -> str:
        ...


class Notifier(Protocol):
    def send_notification(self, recipient: str, message: str) -> None:
        ...


class SupplierProvider(Protocol):
    async def get_stock_info(self, product_id: int) -> dict:
        ...