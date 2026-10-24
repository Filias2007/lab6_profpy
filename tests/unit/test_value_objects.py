import dataclasses

import pytest

from shop.value_objects import Money


def test_money_creation_and_equality():
    assert Money(100.0, "UAH") == Money(100.0, "UAH")


def test_money_default_currency_is_uah():
    assert Money(10.0).currency == "UAH"


def test_money_addition():
    res = Money(100.0, "UAH") + Money(50.0, "UAH")
    assert res.amount == pytest.approx(150.0)
    assert res.currency == "UAH"


def test_money_addition_rounds_to_two_digits():
    res = Money(0.1) + Money(0.2)
    assert res.amount == pytest.approx(0.3)


def test_money_currency_mismatch_raises():
    with pytest.raises(ValueError, match="Currency"):
        Money(100.0, "UAH") + Money(10.0, "USD")


def test_money_is_immutable():
    money = Money(10.0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        money.amount = 20.0  # type: ignore[misc]


@pytest.mark.parametrize(
    "amount",
    [
        pytest.param(0, id="minimum"),
        pytest.param(0.01, id="just-above-minimum"),
        pytest.param(100, id="normal"),
        pytest.param(9999.99, id="large"),
    ],
)
def test_valid_money_amounts(amount):
    assert Money(amount).amount == pytest.approx(amount)


@pytest.mark.parametrize("amount", [-0.01, -1, -10.0, -9999.99])
def test_money_invalid_amount(amount):
    with pytest.raises(ValueError, match="cannot be negative"):
        Money(amount)