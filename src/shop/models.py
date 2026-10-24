from dataclasses import dataclass, field
from shop.value_objects import Money
from shop.exceptions import ProductValidationError

@dataclass
class Product:
    product_id: int
    name: str
    price: Money
    quantity: int
    category: str = "General"

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ProductValidationError("Product name cannot be empty")
        if self.quantity < 0:
            raise ProductValidationError("Quantity cannot be negative")

    @property
    def total_stock_value(self) -> Money:
        return Money(round(self.price.amount * self.quantity, 2), self.price.currency)

@dataclass
class Catalog:
    products: list[Product] = field(default_factory=list)

    def add_product(self, product: Product) -> None:
        self.products.append(product)

    def find_by_id(self, product_id: int) -> Product | None:
        return next((p for p in self.products if p.product_id == product_id), None)

    def filter_by_category(self, category: str) -> list[Product]:
        return [p for p in self.products if p.category.lower() == category.lower()]

    def calculate_total_inventory_value(self) -> float:
        return sum(p.total_stock_value.amount for p in self.products)

    def find_low_stock(self, min_stock: int) -> list[Product]:
        return [p for p in self.products if p.quantity < min_stock]

    def get_most_expensive_product(self) -> Product | None:
        if not self.products:
            return None
        return max(self.products, key=lambda p: p.price.amount)