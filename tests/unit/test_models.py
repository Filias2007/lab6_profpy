import pytest
from shop.models import Product, Cart, Money


def test_money_creation_and_addition():
    m1 = Money(100.0)
    m2 = Money(50.0)
    assert m1.amount == 100.0
    assert (m1 + m2).amount == 150.0


def test_negative_money_rejected():
    with pytest.raises(ValueError, match="negative"):
        Money(-10.0)


def test_product_creation(laptop):
    assert laptop.product_id == 1
    assert laptop.name == "Laptop"
    assert laptop.price.amount == 35000.0


def test_cart_operations(cart):
    assert len(cart) == 2
    assert 1 in cart
    assert 2 in cart
    assert cart.total.amount == pytest.approx(37400.0)


@pytest.mark.parametrize("quantity", [0, -1, -100])
def test_invalid_cart_item_quantity(laptop, quantity):
    c = Cart()
    with pytest.raises(ValueError, match="positive"):
        c.add(laptop, quantity)