import csv
from pathlib import Path
from shop.models import Product, Catalog
from shop.value_objects import Money
from shop.exceptions import ProductValidationError


class ProductRepository:
    def __init__(self, storage_path: Path | None = None) -> None:
        self.storage_path = storage_path
        self._catalog = Catalog()

    def add(self, product: Product) -> None:
        self._catalog.add_product(product)

    def get_all(self) -> list[Product]:
        return self._catalog.products

    def import_from_csv(self, file_path: Path) -> Catalog:
        catalog = Catalog()
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    product = Product(
                        product_id=int(row["id"]),
                        name=row["name"],
                        price=Money(float(row["price"])),
                        quantity=int(row["quantity"]),
                        category=row.get("category", "General"),
                    )
                    catalog.add_product(product)
                except (KeyError, ValueError) as err:
                    raise ProductValidationError(
                        f"Malformed product record: {row}"
                    ) from err
        self._catalog = catalog
        return catalog