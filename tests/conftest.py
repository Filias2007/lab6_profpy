import pytest
from shop.models import Product, Catalog
from shop.value_objects import Money


@pytest.fixture
def product_factory():
    def _create_product(
        product_id: int = 1,
        name: str = "Test Item",
        price: float = 100.0,
        quantity: int = 10,
        category: str = "General"
    ) -> Product:
        return Product(
            product_id=product_id,
            name=name,
            price=Money(price),
            quantity=quantity,
            category=category
        )
    return _create_product


@pytest.fixture
def sample_mouse(product_factory):
    return product_factory(
        product_id=1,
        name="Mouse",
        price=1200.0,
        quantity=50,
        category="Peripherals"
    )


@pytest.fixture
def sample_laptop(product_factory):
    return product_factory(
        product_id=2,
        name="Laptop",
        price=35000.0,
        quantity=5,
        category="Electronics"
    )


@pytest.fixture
def filled_catalog(sample_laptop, product_factory):
    catalog = Catalog()
    catalog.add_product(sample_laptop)
    catalog.add_product(
        product_factory(
            product_id=3,
            name="Phone",
            price=20000.0,
            quantity=10,
            category="Electronics"
        )
    )
    return catalog
