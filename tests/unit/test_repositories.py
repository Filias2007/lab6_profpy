import pytest
from shop.repositories import ProductRepository
from shop.exceptions import ProductValidationError

def test_import_csv_malformed_record_exception_chaining(tmp_path):
    bad_csv = tmp_path / "bad_products.csv"
    bad_csv.write_text("id,name,price,quantity\n1,Keyboard,invalid_price,10\n", encoding="utf-8")

    repo = ProductRepository()
    with pytest.raises(ProductValidationError) as exc_info:
        repo.import_from_csv(bad_csv)
    
    assert exc_info.value.__cause__ is not None
    assert isinstance(exc_info.value.__cause__, ValueError)