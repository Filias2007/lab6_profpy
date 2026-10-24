import pytest

from shop.exceptions import ProductValidationError
from shop.models import Catalog, Product
from shop.value_objects import Money


def test_product_valid_creation(sample_laptop):
    assert sample_laptop.name == "Laptop"
    assert sample_laptop.total_stock_value.amount == pytest.approx(175000.0)


def test_product_default_category(product_factory):
    product = Product(product_id=1, name="Item", price=Money(1.0), quantity=1)
    assert product.category == "General"


def test_empty_product_name_raises_custom_exception():
    with pytest.raises(ProductValidationError, match="cannot be empty"):
        Product(product_id=3, name="   ", price=Money(100.0), quantity=5)


def test_negative_quantity_raises_custom_exception():
    with pytest.raises(ProductValidationError, match="cannot be negative"):
        Product(product_id=4, name="Phone", price=Money(500.0), quantity=-1)


def test_zero_quantity_is_allowed_boundary(product_factory):
    product = product_factory(quantity=0)
    assert product.quantity == 0
    assert product.total_stock_value.amount == 0


def test_negative_price_is_rejected():
    with pytest.raises(ValueError, match="cannot be negative"):
        Product(product_id=5, name="Bad", price=Money(-1.0), quantity=1)


def test_empty_catalog_operations():
    cat = Catalog()
    assert cat.calculate_total_inventory_value() == 0.0
    assert cat.get_most_expensive_product() is None
    assert cat.find_by_id(1) is None
    assert cat.filter_by_category("Any") == []


def test_catalog_add_product(sample_mouse):
    cat = Catalog()
    cat.add_product(sample_mouse)
    assert cat.products == [sample_mouse]


def test_catalog_find_by_id_found_and_missing(filled_catalog, sample_laptop):
    assert filled_catalog.find_by_id(2) is sample_laptop
    assert filled_catalog.find_by_id(999) is None


def test_catalog_filtering_and_max(filled_catalog, sample_laptop):
    electronics = filled_catalog.filter_by_category("Electronics")
    assert len(electronics) == 2
    assert filled_catalog.get_most_expensive_product() == sample_laptop


def test_catalog_filter_is_case_insensitive(filled_catalog):
    assert len(filled_catalog.filter_by_category("electronics")) == 2


def test_catalog_filter_unknown_category(filled_catalog):
    assert filled_catalog.filter_by_category("Garden") == []


def test_catalog_total_inventory_value(filled_catalog):
    # laptop 35000*5 + phone 20000*10
    assert filled_catalog.calculate_total_inventory_value() == pytest.approx(375000.0)


def test_catalog_find_low_stock(filled_catalog):
    low = filled_catalog.find_low_stock(min_stock=6)
    assert [p.name for p in low] == ["Laptop"]
    assert filled_catalog.find_low_stock(min_stock=5) == []


def test_fixture_factory_usage(product_factory):
    cheap = product_factory(product_id=10, price=50.0)
    expensive = product_factory(product_id=11, price=5000.0)
    assert cheap.price.amount < expensive.price.amount