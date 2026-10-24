from dataclasses import dataclass, field


class ProductValidationError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


class PaymentError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class Money:
    amount: float
    currency: str = "UAH"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(round(self.amount + other.amount, 2), self.currency)


@dataclass(frozen=True, slots=True)
class Product:
    product_id: int
    name: str
    price: Money
    quantity: int = 0
    category: str = "General"

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Product name cannot be empty")
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative")


@dataclass
class CartItem:
    product: Product
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")

    @property
    def total(self) -> Money:
        return Money(
            self.product.price.amount * self.quantity,
            self.product.price.currency,
        )


@dataclass
class Cart:
    items: list[CartItem] = field(default_factory=list)

    def add(self, product: Product, quantity: int = 1) -> None:
        self.items.append(CartItem(product, quantity))

    def __len__(self) -> int:
        return len(self.items)

    def __contains__(self, product_id: int) -> bool:
        return any(item.product.product_id == product_id for item in self.items)

    @property
    def total(self) -> Money:
        return Money(sum(item.total.amount for item in self.items))