import pytest
from shop.value_objects import Money

def test_money_creation():
    m = Money(150.50, "UAH")
    assert m.amount == 150.50
    assert m.currency == "UAH"

def test_negative_money_raises_exception():
    with pytest.raises(ValueError, match="cannot be negative"):
        Money(-10.0, "UAH")

def test_money_addition():
    m1 = Money(100.0, "UAH")
    m2 = Money(50.25, "UAH")
    res = m1 + m2
    assert res.amount == pytest.approx(150.25)

def test_money_currency_mismatch():
    m1 = Money(100.0, "UAH")
    m2 = Money(100.0, "USD")
    with pytest.raises(ValueError, match="Currency mismatch"):
        m1 + m2

@pytest.mark.parametrize("amount, expected", [
    (0.0, 0.0),
    (0.01, 0.01),
    (999.99, 999.99),
])
def test_money_boundary_amounts(amount, expected):
    m = Money(amount)
    assert m.amount == pytest.approx(expected)