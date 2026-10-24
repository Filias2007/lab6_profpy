import pytest
from shop.value_objects import Money

def test_money_creation_and_equality():
    m1 = Money(100.0, "UAH")
    m2 = Money(100.0, "UAH")
    assert m1 == m2

def test_money_addition():
    m1 = Money(100.0, "UAH")
    m2 = Money(50.0, "UAH")
    res = m1 + m2
    assert res.amount == 150.0

def test_money_invalid_amount():
    with pytest.raises(ValueError, match="cannot be negative"):
        Money(-10.0)