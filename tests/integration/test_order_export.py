import pytest
import json
from shop.repositories import ProductRepository
from shop.services import OrderService
from shop.exporters import export_catalog_to_json
from unittest.mock import Mock

@pytest.mark.integration
def test_order_export_integration(tmp_path):
    csv_file = tmp_path / "import_products.csv"
    csv_file.write_text(
        "id,name,price,quantity,category\n"
        "101,Monitor,8500.0,10,Peripherals\n"
        "102,Headphones,2500.0,20,Audio\n",
        encoding="utf-8"
    )

    repo = ProductRepository()
    catalog = repo.import_from_csv(csv_file)
    assert len(catalog.products) == 2

    monitor = catalog.find_by_id(101)
    mock_gateway = Mock()
    mock_gateway.pay.return_value = "PAY-INT-100"
    mock_notifier = Mock()

    order_service = OrderService(mock_gateway, mock_notifier)
    payment_id = order_service.checkout("client@domain.com", monitor, quantity=2)

    assert payment_id == "PAY-INT-100"
    assert monitor.quantity == 8

    json_file = tmp_path / "exported_catalog.json"
    export_catalog_to_json(catalog, json_file)

    assert json_file.exists()
    exported_data = json.loads(json_file.read_text(encoding="utf-8"))
    assert len(exported_data) == 2
    assert exported_data[0]["quantity"] == 8
    assert exported_data[0]["stock_value"] == pytest.approx(68000.0)