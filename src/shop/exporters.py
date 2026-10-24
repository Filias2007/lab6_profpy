import json
from pathlib import Path


def export_order(order_data: dict, output_path: Path) -> None:
    output_path.write_text(
        json.dumps(order_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )