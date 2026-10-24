import json
from pathlib import Path
from shop.models import Catalog

def export_catalog_to_json(catalog: Catalog, output_path: Path) -> None:
    data = [
        {
            "id": p.product_id,
            "name": p.name,
            "price": p.price.amount,
            "currency": p.price.currency,
            "quantity": p.quantity,
            "category": p.category,
            "stock_value": p.total_stock_value.amount
        }
        for p in catalog.products
    ]
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")