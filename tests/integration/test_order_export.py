import json
from unittest.mock import Mock

import pytest

from shop.exporters import export_catalog_to_json
from shop.repositories import ProductRepository
from shop.services import OrderService


@pytest.mark.integration
def test_order_export_integration(tmp_path):
    csv_file = tmp_path / "import_products.csv"
    csv_file.write_text(
        "id,name,price,quantity,category\n"
        "101,Monitor,8500.0,10,Peripherals\n"
        "102,Headphones,2500.0,20,Audio\n",
        encoding="utf-8",
    )

    repo = ProductRepository()
    catalog = repo.import_from_csv(csv_file)
    assert len(catalog.products) == 2

    monitor = catalog.find_by_id(101)
    mock_gateway = Mock()
    mock_gateway.pay.return_value = "PAY-INT-100"
    mock_notifier = Mock()

    payment_id = OrderService(mock_gateway, mock_notifier).checkout(
        "client@domain.com", monitor, quantity=2
    )

    assert payment_id == "PAY-INT-100"
    assert monitor.quantity == 8
    mock_gateway.pay.assert_called_once_with(17000.0)
    mock_notifier.send_notification.assert_called_once_with(
        "client@domain.com", "Order confirmed: PAY-INT-100"
    )

    json_file = tmp_path / "exported_catalog.json"
    export_catalog_to_json(catalog, json_file)

    exported = {item["id"]: item for item in json.loads(json_file.read_text(encoding="utf-8"))}
    assert set(exported) == {101, 102}
    assert exported[101]["quantity"] == 8
    assert exported[101]["stock_value"] == pytest.approx(68000.0)
    assert exported[102]["stock_value"] == pytest.approx(50000.0)