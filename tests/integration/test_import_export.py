import json
import pytest
from unittest.mock import Mock
from shop.repositories import ProductRepository
from shop.services import CheckoutService, PaymentGateway, Notifier
from shop.exporters import export_order
from shop.models import Cart


@pytest.mark.integration
def test_import_export_pipeline_integration(tmp_path):
    csv_file = tmp_path / "products.csv"
    csv_file.write_text(
        "id,name,price,quantity,category\n"
        "101,Keyboard,1500.0,10,Peripherals\n"
        "102,Headphones,3000.0,5,Audio\n",
        encoding="utf-8",
    )

    repo = ProductRepository()
    products = repo.import_from_csv(csv_file)
    assert len(products) == 2

    cart = Cart()
    cart.add(products[0], 2)

    gateway = Mock(spec=PaymentGateway)
    gateway.pay.return_value = "PAY-INT-500"
    notifier = Mock(spec=Notifier)

    service = CheckoutService(gateway, notifier)
    payment_id = service.checkout("client@test.com", cart)

    output_json = tmp_path / "order.json"
    export_order(
        {
            "payment_id": payment_id,
            "total": cart.total.amount,
        },
        output_json,
    )

    assert output_json.exists()
    data = json.loads(output_path=output_json.read_text(encoding="utf-8"))
    assert data["payment_id"] == "PAY-INT-500"
    assert data["total"] == pytest.approx(3000.0)