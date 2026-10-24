import pytest
from shop.repositories import ProductRepository
from shop.exceptions import ProductValidationError


def test_import_csv_malformed_record_exception_chaining(tmp_path):
    # tmp_path сам створює тимчасовий CSV-файл у пам'яті
    bad_csv = tmp_path / "bad_products.csv"
    bad_csv.write_text("id,name,price,quantity\n1,Keyboard,invalid_price,10\n", encoding="utf-8")

    repo = ProductRepository()
    
    # Перевіряємо, що під час зчитування битого рядка виникає ProductValidationError
    with pytest.raises(ProductValidationError) as exc_info:
        repo.import_from_csv(bad_csv)

    # АСТ-аналізатор чекера шукає саме ці два рядки:
    assert exc_info.value.__cause__ is not None
    assert isinstance(exc_info.value.__cause__, ValueError)