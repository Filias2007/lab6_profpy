import pytest
from shop.models import Product, Money, ProductValidationError
from shop.repositories import ProductRepository


def test_product_empty_name_validation():
    with pytest.raises(ValueError, match="cannot be empty"):
        Product(product_id=1, name="", price=Money(100.0))


def test_product_negative_quantity_validation():
    with pytest.raises(ValueError, match="cannot be negative"):
        Product(product_id=1, name="Item", price=Money(100.0), quantity=-1)


def test_repository_import_csv_malformed_exception_chaining(tmp_path):
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("id,name,price,quantity\n1,Key,invalid_price,10\n", encoding="utf-8")

    repo = ProductRepository()
    with pytest.raises(ProductValidationError) as exc_info:
        repo.import_from_csv(bad_csv)

    assert exc_info.value.__cause__ is not None
    assert isinstance(exc_info.value.__cause__, ValueError)