from unittest.mock import AsyncMock, Mock, create_autospec

import pytest

from shop.exceptions import InsufficientStockError, PaymentError
from shop.protocols import Notifier, PaymentGateway, SupplierProvider
from shop.services import AsyncSupplierService, DiscountService, OrderService


@pytest.fixture
def gateway():
    return create_autospec(PaymentGateway, instance=True)


@pytest.fixture
def notifier():
    return create_autospec(Notifier, instance=True)


@pytest.fixture
def order_service(gateway, notifier):
    return OrderService(payment_gateway=gateway, notifier=notifier)


# ---------- DiscountService ----------

@pytest.mark.parametrize(
    "percent, expected_price",
    [(0, 100.0), (10, 90.0), (25, 75.0), (100, 0.0)],
)
def test_discount_service_parametrize(product_factory, percent, expected_price):
    product = product_factory(price=100.0)
    res = DiscountService().apply_percentage_discount(product, percent)
    assert res == pytest.approx(expected_price)


@pytest.mark.parametrize("percent", [-0.01, -1, 100.01, 150.0])
def test_invalid_discount_raises_exception(product_factory, percent):
    product = product_factory(price=100.0)
    with pytest.raises(ValueError, match="between 0 and 100"):
        DiscountService().apply_percentage_discount(product, percent)


def test_discount_does_not_change_product_price(product_factory):
    product = product_factory(price=100.0)
    DiscountService().apply_percentage_discount(product, 50)
    assert product.price.amount == pytest.approx(100.0)


# ---------- OrderService ----------

def test_checkout_success_mock(sample_mouse, order_service, gateway, notifier):
    gateway.pay.return_value = "PAY-001"

    payment_id = order_service.checkout("customer@test.com", sample_mouse, quantity=2)

    assert payment_id == "PAY-001"
    assert sample_mouse.quantity == 48
    gateway.pay.assert_called_once_with(2400.0)
    notifier.send_notification.assert_called_once_with(
        "customer@test.com", "Order confirmed: PAY-001"
    )


def test_checkout_exact_stock_boundary(product_factory, order_service, gateway):
    gateway.pay.return_value = "PAY-ALL"
    product = product_factory(quantity=3)
    order_service.checkout("a@b.com", product, quantity=3)
    assert product.quantity == 0


def test_checkout_one_more_than_stock_fails(product_factory, order_service):
    product = product_factory(quantity=3)
    with pytest.raises(InsufficientStockError, match="Not enough stock"):
        order_service.checkout("a@b.com", product, quantity=4)
    assert product.quantity == 3


def test_checkout_payment_failure_side_effect(sample_laptop, order_service, gateway, notifier):
    gateway.pay.side_effect = PaymentError("Gateway error")

    with pytest.raises(PaymentError, match="Gateway error"):
        order_service.checkout("customer@test.com", sample_laptop, quantity=1)

    notifier.send_notification.assert_not_called()
    assert sample_laptop.quantity == 5


def test_checkout_notifier_failure_propagates(sample_mouse, order_service, gateway, notifier):
    gateway.pay.return_value = "PAY-002"
    notifier.send_notification.side_effect = ConnectionError("SMTP down")

    with pytest.raises(ConnectionError, match="SMTP down"):
        order_service.checkout("customer@test.com", sample_mouse, quantity=1)

    gateway.pay.assert_called_once_with(1200.0)


def test_checkout_insufficient_stock_has_no_side_effects(sample_laptop, order_service, gateway, notifier):
    with pytest.raises(InsufficientStockError, match="Not enough stock"):
        order_service.checkout("customer@test.com", sample_laptop, quantity=100)

    gateway.pay.assert_not_called()
    notifier.send_notification.assert_not_called()


@pytest.mark.parametrize("quantity", [0, -1, -100])
def test_checkout_non_positive_quantity_rejected(sample_mouse, order_service, gateway, quantity):
    with pytest.raises(ValueError, match="positive"):
        order_service.checkout("customer@test.com", sample_mouse, quantity=quantity)

    gateway.pay.assert_not_called()
    assert sample_mouse.quantity == 50


def test_checkout_with_plain_mock(sample_mouse):
    mock_gateway = Mock()
    mock_gateway.pay.side_effect = ["PAY-1", "PAY-2"]
    mock_notifier = Mock()
    service = OrderService(mock_gateway, mock_notifier)

    assert service.checkout("x@y.com", sample_mouse, 1) == "PAY-1"
    assert service.checkout("x@y.com", sample_mouse, 1) == "PAY-2"
    assert mock_notifier.send_notification.call_count == 2
    assert sample_mouse.quantity == 48


# ---------- AsyncSupplierService ----------

@pytest.mark.asyncio
async def test_async_supplier_service():
    mock_provider = AsyncMock(spec=SupplierProvider)
    mock_provider.get_stock_info.return_value = {"available_stock": 100}

    result = await AsyncSupplierService(mock_provider).fetch_external_stock(product_id=1)

    assert result == 100
    mock_provider.get_stock_info.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_async_supplier_missing_key_defaults_to_zero():
    mock_provider = AsyncMock()
    mock_provider.get_stock_info.return_value = {}

    assert await AsyncSupplierService(mock_provider).fetch_external_stock(7) == 0


@pytest.mark.asyncio
async def test_async_supplier_failure_path():
    mock_provider = AsyncMock()
    mock_provider.get_stock_info.side_effect = ConnectionError("Network error")

    with pytest.raises(ConnectionError, match="Network error"):
        await AsyncSupplierService(mock_provider).fetch_external_stock(1)
    mock_provider.get_stock_info.assert_awaited_once_with(1)