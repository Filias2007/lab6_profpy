import pytest
from unittest.mock import Mock, AsyncMock
from shop.models import Money, Cart
from shop.services import (
    PercentageDiscount,
    CheckoutService,
    PaymentGateway,
    Notifier,
    PaymentError,
    AsyncSupplierService,
)


@pytest.mark.parametrize(
    ("percent", "expected"),
    [
        (0, 100.0),
        (10, 90.0),
        (25, 75.0),
        (100, 0.0),
    ],
)
def test_percentage_discount(percent, expected):
    discount = PercentageDiscount(percent)
    result = discount.apply(Money(100.0))
    assert result.amount == pytest.approx(expected)


def test_invalid_percentage_discount():
    with pytest.raises(ValueError, match="Invalid discount"):
        PercentageDiscount(150.0)


def test_checkout_success(cart):
    gateway = Mock(spec=PaymentGateway)
    gateway.pay.return_value = "PAY-001"
    notifier = Mock(spec=Notifier)

    service = CheckoutService(payment_gateway=gateway, notifier=notifier)
    result = service.checkout("test@example.com", cart)

    assert result == "PAY-001"
    gateway.pay.assert_called_once_with(37400.0)
    notifier.send_notification.assert_called_once_with(
        "test@example.com", "Payment successful: PAY-001"
    )


def test_checkout_payment_failure(cart):
    gateway = Mock(spec=PaymentGateway)
    gateway.pay.side_effect = PaymentError("Service Unavailable")
    notifier = Mock(spec=Notifier)

    service = CheckoutService(payment_gateway=gateway, notifier=notifier)

    with pytest.raises(PaymentError, match="Service Unavailable"):
        service.checkout("test@example.com", cart)

    notifier.send_notification.assert_not_called()


def test_checkout_empty_cart():
    gateway = Mock(spec=PaymentGateway)
    notifier = Mock(spec=Notifier)
    service = CheckoutService(gateway, notifier)

    with pytest.raises(ValueError, match="empty"):
        service.checkout("test@example.com", Cart())


@pytest.mark.asyncio
async def test_async_supplier_service():
    mock_provider = AsyncMock()
    mock_provider.get_stock_info.return_value = {"available_stock": 42}

    service = AsyncSupplierService(mock_provider)
    res = await service.fetch_external_stock(product_id=10)

    assert res == 42
    mock_provider.get_stock_info.assert_awaited_once_with(10)