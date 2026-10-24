import pytest
from unittest.mock import Mock, AsyncMock
from shop.services import OrderService, AsyncSupplierService, DiscountService
from shop.exceptions import PaymentError, InsufficientStockError
from shop.value_objects import Money

# 1. Перевірка return_value
def test_checkout_success_return_value(sample_mouse):
    mock_gateway = Mock()
    mock_gateway.pay.return_value = "PAY-12345"
    mock_notifier = Mock()

    service = OrderService(payment_gateway=mock_gateway, notifier=mock_notifier)
    result = service.checkout("test@example.com", sample_mouse, quantity=1)

    assert result == "PAY-12345"
    mock_gateway.pay.assert_called_once_with(1200.0)

# 2. Перевірка side_effect та assert_not_called
def test_checkout_payment_failure_side_effect(sample_laptop):
    mock_gateway = Mock()
    mock_gateway.pay.side_effect = PaymentError("Gateway failure")
    mock_notifier = Mock()

    service = OrderService(payment_gateway=mock_gateway, notifier=mock_notifier)

    with pytest.raises(PaymentError, match="Gateway failure"):
        service.checkout("test@example.com", sample_laptop, quantity=1)

    mock_notifier.send_notification.assert_not_called()

# 3. Перевірка AsyncMock та assert_awaited_once_with
@pytest.mark.asyncio
async def test_async_supplier_fetch_stock():
    mock_provider = AsyncMock()
    mock_provider.get_stock_info.return_value = {"available_stock": 42}

    service = AsyncSupplierService(mock_provider)
    res = await service.fetch_external_stock(product_id=10)

    assert res == 42
    mock_provider.get_stock_info.assert_awaited_once_with(10)