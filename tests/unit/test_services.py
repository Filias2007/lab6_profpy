import pytest
from unittest.mock import Mock, AsyncMock
from shop.services import OrderService, AsyncSupplierService
from shop.exceptions import PaymentError

def test_checkout_payment_failure_side_effect(sample_laptop):
    mock_gateway = Mock()
    mock_gateway.pay.side_effect = PaymentError("Gateway unavailable")
    mock_notifier = Mock()

    order_service = OrderService(payment_gateway=mock_gateway, notifier=mock_notifier)

    with pytest.raises(PaymentError, match="Gateway unavailable"):
        order_service.checkout("customer@example.com", sample_laptop, quantity=1)

    # Обов'язкова перевірка відсутності виклику
    mock_notifier.send_notification.assert_not_called()

@pytest.mark.asyncio
async def test_async_supplier_service_fetch_stock():
    mock_provider = AsyncMock()
    mock_provider.get_stock_info.return_value = {"available_stock": 100}

    service = AsyncSupplierService(mock_provider)
    result = await service.fetch_external_stock(product_id=1)

    assert result == 100
    mock_provider.get_stock_info.assert_awaited_once_with(1)