import pytest
from shop.models import Product, Cart, Money


@pytest.fixture
def laptop() -> Product:
    return Product(
        product_id=1,
        name="Laptop",
        price=Money(35000.0),
        quantity=5,
        category="Electronics",
    )


@pytest.fixture
def mouse() -> Product:
    return Product(
        product_id=2,
        name="Mouse",
        price=Money(1200.0),
        quantity=20,
        category="Peripherals",
    )


@pytest.fixture
def cart(laptop, mouse) -> Cart:
    c = Cart()
    c.add(laptop, 1)
    c.add(mouse, 2)
    return c