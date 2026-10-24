import pytest
from shop.models import Product, Catalog
from shop.value_objects import Money
from shop.exceptions import ProductValidationError

def test_product_valid_creation(sample_laptop):
    assert sample_laptop.name == "Laptop"
    assert sample_laptop.total_stock_value.amount == pytest.approx(175000.0)

def test_empty_product_name_raises_custom_exception():
    with pytest.raises(ProductValidationError, match="cannot be empty"):
        Product(product_id=3, name="   ", price=Money(100.0), quantity=5)

def test_negative_quantity_raises_custom_exception():
    with pytest.raises(ProductValidationError, match="cannot be negative"):
        Product(product_id=4, name="Phone", price=Money(500.0), quantity=-1)

def test_empty_catalog_operations():
    cat = Catalog()
    assert cat.calculate_total_inventory_value() == 0.0
    assert cat.get_most_expensive_product() is None

def test_catalog_filtering_and_max(filled_catalog, sample_laptop):
    electronics = filled_catalog.filter_by_category("Electronics")
    assert len(electronics) == 2
    most_expensive = filled_catalog.get_most_expensive_product()
    assert most_expensive == sample_laptop

def test_fixture_factory_usage(product_factory):
    cheap = product_factory(product_id=10, price=50.0)
    expensive = product_factory(product_id=11, price=5000.0)
    assert cheap.price.amount < expensive.price.amount