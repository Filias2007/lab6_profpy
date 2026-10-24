import pytest
from unittest.mock import Mock, AsyncMock
from shop.services import DiscountService, OrderService, AsyncSupplierService
from shop.exceptions import PaymentError, InsufficientStockError


@pytest.mark.parametrize("percent, expected_price", [
    (0, 100.0),
    (10, 90.0),
    (25, 75.0),
    (100, 0.0),
])
def test_discount_service_parametrize(product_factory, percent, expected_price):
    product = product_factory(price=100.0)
    service = DiscountService()
    res = service.apply_percentage_discount(product, percent)
    assert res == pytest.approx(expected_price)


def test_invalid_discount_raises_exception(product_factory):
    product = product_factory(price=100.0)
    service = DiscountService()
    with pytest.raises(ValueError, match="between 0 and 100"):
        service.apply_percentage_discount(product, 150.0)


def test_checkout_success_mock(sample_mouse):
    mock_gateway = Mock()
    mock_gateway.pay.return_value = "PAY-001"
    mock_notifier = Mock()

    order_service = OrderService(payment_gateway=mock_gateway, notifier=mock_notifier)
    payment_id = order_service.checkout("customer@test.com", sample_mouse, quantity=2)

    assert payment_id == "PAY-001"
    assert sample_mouse.quantity == 48
    mock_gateway.pay.assert_called_once_with(2400.0)
    mock_notifier.send_notification.assert_called_once_with("customer@test.com", "Order confirmed: PAY-001")


def test_checkout_payment_failure_side_effect(sample_laptop):
    mock_gateway = Mock()
    mock_gateway.pay.side_effect = PaymentError("Gateway error")
    mock_notifier = Mock()

    order_service = OrderService(payment_gateway=mock_gateway, notifier=mock_notifier)

    with pytest.raises(PaymentError, match="Gateway error"):
        order_service.checkout("customer@test.com", sample_laptop, quantity=1)

    mock_notifier.send_notification.assert_not_called()


def test_checkout_insufficient_stock(sample_laptop):
    mock_gateway = Mock()
    mock_notifier = Mock()
    order_service = OrderService(mock_gateway, mock_notifier)

    with pytest.raises(InsufficientStockError, match="Not enough stock"):
        order_service.checkout("customer@test.com", sample_laptop, quantity=100)


@pytest.mark.asyncio
async def test_async_supplier_service():
    mock_provider = AsyncMock()
    mock_provider.get_stock_info.return_value = {"available_stock": 100}

    service = AsyncSupplierService(mock_provider)
    result = await service.fetch_external_stock(product_id=1)

    assert result == 100
    mock_provider.get_stock_info.assert_awaited_once_with(1)