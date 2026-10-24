import pytest
from shop.repositories import ProductRepository
from shop.exceptions import ProductValidationError

def test_import_from_csv_malformed_record_exception_chaining(tmp_path):
    csv_file = tmp_path / "bad_products.csv"
    csv_file.write_text("id,name,price,quantity\n1,Keyboard,invalid_price,10\n", encoding="utf-8")

    repo = ProductRepository()
    with pytest.raises(ProductValidationError) as exc_info:
        repo.import_from_csv(csv_file)
    
    assert isinstance(exc_info.value.__cause__, ValueError)