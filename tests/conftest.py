import pytest
from shop.models import Product, Catalog
from shop.value_objects import Money

@pytest.fixture
def sample_laptop() -> Product:
    return Product(
        product_id=1,
        name="Gaming Laptop",
        price=Money(45000.0, "UAH"),
        quantity=10,
        category="Electronics"
    )

@pytest.fixture
def sample_mouse() -> Product:
    return Product(
        product_id=2,
        name="Wireless Mouse",
        price=Money(1200.0, "UAH"),
        quantity=50,
        category="Electronics"
    )

@pytest.fixture
def filled_catalog(sample_laptop, sample_mouse) -> Catalog:
    catalog = Catalog()
    catalog.add_product(sample_laptop)
    catalog.add_product(sample_mouse)
    return catalog

@pytest.fixture
def product_factory():
    """Fixture Factory для динамічного створення товарів у тестах."""
    def _create_product(product_id: int = 1, name: str = "Test Item", price: float = 100.0, quantity: int = 5):
        return Product(
            product_id=product_id,
            name=name,
            price=Money(price, "UAH"),
            quantity=quantity
        )
    return _create_product