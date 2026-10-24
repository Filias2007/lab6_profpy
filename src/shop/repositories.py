import csv
from pathlib import Path
from shop.models import Product, Money, ProductValidationError


class ProductRepository:
    def import_from_csv(self, file_path: Path) -> list[Product]:
        products = []
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
                    products.append(product)
                except (KeyError, ValueError) as err:
                    raise ProductValidationError("Malformed CSV record") from err
        return products