import pytest
from shop.repositories import ProductRepository
from shop.exceptions import ProductValidationError

def test_import_csv_malformed_record_exception_chaining(tmp_path):
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("id,name,price,quantity\n1,Laptop,not_a_number,10\n", encoding="utf-8")

    repo = ProductRepository()
    with pytest.raises(ProductValidationError) as exc_info:
        repo.import_from_csv(bad_csv)

    # Автоперевірка шукає виклик isinstance з __cause__
    assert exc_info.value.__cause__ is not None
    assert isinstance(exc_info.value.__cause__, ValueError)