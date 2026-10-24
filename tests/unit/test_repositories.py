import pytest

from shop.exceptions import ProductValidationError
from shop.repositories import ProductRepository


def test_repository_add_and_get_all(sample_mouse, sample_laptop):
    repo = ProductRepository()
    repo.add(sample_mouse)
    repo.add(sample_laptop)
    assert repo.get_all() == [sample_mouse, sample_laptop]


def test_import_csv_valid(tmp_path):
    csv_file = tmp_path / "ok.csv"
    csv_file.write_text(
        "id,name,price,quantity,category\n1,Mouse,1200.5,3,Peripherals\n",
        encoding="utf-8",
    )
    repo = ProductRepository()
    catalog = repo.import_from_csv(csv_file)

    assert len(catalog.products) == 1
    product = catalog.products[0]
    assert product.name == "Mouse"
    assert product.price.amount == pytest.approx(1200.5)
    assert product.quantity == 3
    assert repo.get_all() == catalog.products


def test_import_csv_without_category_uses_default(tmp_path):
    csv_file = tmp_path / "nocat.csv"
    csv_file.write_text("id,name,price,quantity\n1,Cable,50,10\n", encoding="utf-8")
    catalog = ProductRepository().import_from_csv(csv_file)
    assert catalog.products[0].category == "General"


def test_import_csv_header_only_gives_empty_catalog(tmp_path):
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("id,name,price,quantity\n", encoding="utf-8")
    assert ProductRepository().import_from_csv(csv_file).products == []


def test_import_csv_malformed_record_exception_chaining(tmp_path):
    bad_csv = tmp_path / "bad_products.csv"
    bad_csv.write_text(
        "id,name,price,quantity\n1,Keyboard,invalid_price,10\n", encoding="utf-8"
    )
    repo = ProductRepository()
    with pytest.raises(ProductValidationError) as exc_info:
        repo.import_from_csv(bad_csv)

    assert isinstance(exc_info.value.__cause__, ValueError)


def test_import_csv_missing_column_raises_validation_error(tmp_path):
    bad_csv = tmp_path / "missing.csv"
    bad_csv.write_text("id,name,price\n1,Keyboard,100\n", encoding="utf-8")
    with pytest.raises(ProductValidationError, match="Malformed") as exc_info:
        ProductRepository().import_from_csv(bad_csv)
    assert isinstance(exc_info.value.__cause__, KeyError)


@pytest.mark.parametrize(
    "row",
    [
        pytest.param("1,Item,-5,1", id="negative-price"),
        pytest.param("1,Item,10,abc", id="non-numeric-quantity"),
        pytest.param("x,Item,10,1", id="non-numeric-id"),
    ],
)
def test_import_csv_invalid_rows(tmp_path, row):
    bad_csv = tmp_path / "invalid.csv"
    bad_csv.write_text(f"id,name,price,quantity\n{row}\n", encoding="utf-8")
    with pytest.raises(ProductValidationError):
        ProductRepository().import_from_csv(bad_csv)


def test_import_csv_negative_quantity_raises_custom_error(tmp_path):
    bad_csv = tmp_path / "negqty.csv"
    bad_csv.write_text("id,name,price,quantity\n1,Item,10,-1\n", encoding="utf-8")
    with pytest.raises(ProductValidationError):
        ProductRepository().import_from_csv(bad_csv)


def test_failed_import_keeps_previous_catalog(tmp_path, sample_mouse):
    repo = ProductRepository()
    repo.add(sample_mouse)
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("id,name,price,quantity\n1,X,oops,1\n", encoding="utf-8")
    with pytest.raises(ProductValidationError):
        repo.import_from_csv(bad_csv)
    assert repo.get_all() == [sample_mouse]


def test_import_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        ProductRepository().import_from_csv(tmp_path / "nope.csv")