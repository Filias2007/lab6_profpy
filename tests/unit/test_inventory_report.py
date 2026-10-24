from unittest.mock import MagicMock, Mock, create_autospec, patch

import pytest

from shop import services
from shop.models import Catalog
from shop.protocols import Notifier
from shop.repositories import ProductRepository
from shop.services import InventoryReportService


class FakeProductRepository:
    """Fake: проста in-memory реалізація інтерфейсу ProductRepository."""

    def __init__(self, products=None):
        self.items = list(products or [])

    def add(self, product):
        self.items.append(product)

    def get_all(self):
        return self.items


@pytest.fixture
def notifier():
    return create_autospec(Notifier, instance=True)


@pytest.fixture
def low_and_ok_products(product_factory):
    return [
        product_factory(product_id=1, name="Cable", quantity=1),
        product_factory(product_id=2, name="Mouse", quantity=4),
        product_factory(product_id=3, name="Phone", quantity=50),
    ]


# ---------- Mock репозиторію ----------

def test_find_low_stock_with_mock_repository(product_factory):
    repo = create_autospec(ProductRepository, instance=True)
    repo.get_all.return_value = [
        product_factory(product_id=1, name="A", quantity=1),
        product_factory(product_id=2, name="B", quantity=10),
    ]
    service = InventoryReportService(repo, Mock(), min_stock=5)

    assert service.find_low_stock_names() == ["A"]
    repo.get_all.assert_called_once_with()


def test_repository_called_each_time_spy(low_and_ok_products):
    spy = Mock(wraps=FakeProductRepository(low_and_ok_products))
    service = InventoryReportService(spy, Mock(), min_stock=5)

    assert service.find_low_stock_names() == ["Cable", "Mouse"]
    assert service.find_low_stock_names() == ["Cable", "Mouse"]
    assert spy.get_all.call_count == 2


# ---------- Fake репозиторію ----------

def test_notify_low_stock_with_fake_repository(low_and_ok_products, notifier):
    repo = FakeProductRepository(low_and_ok_products)
    service = InventoryReportService(repo, notifier, min_stock=5)

    count = service.notify_low_stock("manager@shop.com")

    assert count == 2
    notifier.send_notification.assert_called_once_with(
        "manager@shop.com", "Low stock: Cable, Mouse"
    )


def test_no_low_stock_sends_nothing(product_factory, notifier):
    repo = FakeProductRepository([product_factory(quantity=100)])
    service = InventoryReportService(repo, notifier, min_stock=5)

    assert service.notify_low_stock("manager@shop.com") == 0
    notifier.send_notification.assert_not_called()


def test_empty_repository_has_no_low_stock(notifier):
    service = InventoryReportService(FakeProductRepository(), notifier, min_stock=5)
    assert service.find_low_stock_names() == []


def test_notifier_failure_propagates(low_and_ok_products, notifier):
    notifier.send_notification.side_effect = ConnectionError("SMTP down")
    service = InventoryReportService(
        FakeProductRepository(low_and_ok_products), notifier, min_stock=5
    )
    with pytest.raises(ConnectionError, match="SMTP down"):
        service.notify_low_stock("manager@shop.com")


def test_notification_message_with_magicmock(low_and_ok_products):
    notifier = MagicMock()
    service = InventoryReportService(
        FakeProductRepository(low_and_ok_products), notifier, min_stock=2
    )

    service.notify_low_stock("m@shop.com")

    args, _ = notifier.send_notification.call_args
    assert args == ("m@shop.com", "Low stock: Cable")


# ---------- Граничні значення (parametrize з ids) ----------

@pytest.mark.parametrize(
    "min_stock, expected",
    [
        pytest.param(0, [], id="zero-threshold"),
        pytest.param(5, [], id="equal-is-not-low"),
        pytest.param(6, ["Item"], id="just-below-threshold"),
    ],
)
def test_low_stock_threshold_boundaries(product_factory, min_stock, expected):
    repo = FakeProductRepository([product_factory(name="Item", quantity=5)])
    service = InventoryReportService(repo, Mock(), min_stock=min_stock)
    assert service.find_low_stock_names() == expected


# ---------- Конфігурація: monkeypatch / patch ----------

def test_default_min_stock_from_env(monkeypatch):
    monkeypatch.setenv("SHOP_MIN_STOCK", "7")
    service = InventoryReportService(FakeProductRepository(), Mock())
    assert service.min_stock == 7


def test_default_min_stock_without_env():
    service = InventoryReportService(FakeProductRepository(), Mock())
    assert service.min_stock == 5


def test_min_stock_with_monkeypatch_setattr(monkeypatch):
    monkeypatch.setattr(services, "load_config", lambda: {"min_stock": 9})
    service = InventoryReportService(FakeProductRepository(), Mock())
    assert service.min_stock == 9


def test_min_stock_with_patch():
    with patch("shop.services.load_config", return_value={"min_stock": 2}) as cfg:
        service = InventoryReportService(FakeProductRepository(), Mock())
    assert service.min_stock == 2
    cfg.assert_called_once_with()


def test_explicit_min_stock_does_not_read_config():
    with patch("shop.services.load_config") as cfg:
        InventoryReportService(FakeProductRepository(), Mock(), min_stock=0)
    cfg.assert_not_called()


# ---------- Fixtures: параметризована, module, yield ----------

def test_filter_by_parameterized_category(category, product_factory):
    catalog = Catalog()
    catalog.add_product(product_factory(product_id=1, category=category))
    catalog.add_product(product_factory(product_id=2, category="Other"))
    assert len(catalog.filter_by_category(category)) == 1


def test_module_scoped_csv_text(tmp_path, products_csv_text):
    csv_file = tmp_path / "p.csv"
    csv_file.write_text(products_csv_text, encoding="utf-8")
    catalog = ProductRepository().import_from_csv(csv_file)
    assert [p.name for p in catalog.products] == ["Cable", "Mouse", "Phone"]


def test_yield_fixture_report_file(opened_report, tmp_path):
    opened_report.write("Low stock: Cable")
    opened_report.flush()
    assert not opened_report.closed
    assert (tmp_path / "report.txt").read_text(encoding="utf-8") == "Low stock: Cable"