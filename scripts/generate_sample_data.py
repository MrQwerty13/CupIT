"""Generate a deterministic, realistic local demo dataset for CupIT."""

from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "samples"

PRODUCTS = [
    {"id": "espresso", "name": "Эспрессо", "category": "Кофе", "current_price": 190, "current_cost": 42, "active": True},
    {"id": "americano", "name": "Американо", "category": "Кофе", "current_price": 220, "current_cost": 48, "active": True},
    {"id": "cappuccino", "name": "Капучино", "category": "Кофе с молоком", "current_price": 310, "current_cost": 92, "active": True},
    {"id": "flat-white", "name": "Флэт уайт", "category": "Кофе с молоком", "current_price": 350, "current_cost": 116, "active": True},
    {"id": "latte", "name": "Латте", "category": "Кофе с молоком", "current_price": 340, "current_cost": 108, "active": True},
    {"id": "filter", "name": "Фильтр-кофе", "category": "Альтернатива", "current_price": 250, "current_cost": 63, "active": True},
    {"id": "croissant", "name": "Круассан", "category": "Выпечка", "current_price": 260, "current_cost": 124, "active": True},
    {"id": "syrniki", "name": "Сырники", "category": "Завтраки", "current_price": 480, "current_cost": 205, "active": True},
    {"id": "sandwich", "name": "Сэндвич с индейкой", "category": "Еда", "current_price": 430, "current_cost": 218, "active": True},
    {"id": "cookie", "name": "Печенье шоколадное", "category": "Десерты", "current_price": 180, "current_cost": 72, "active": True},
]


def build_receipts() -> list[dict[str, object]]:
    product_by_id = {item["id"]: item for item in PRODUCTS}
    coffee = ["cappuccino", "flat-white", "latte", "filter", "americano", "espresso"]
    food = ["croissant", "syrniki", "sandwich", "cookie"]
    receipts: list[dict[str, object]] = []
    start = date(2026, 7, 4)
    for day_offset in range(42):
        business_day = start + timedelta(days=day_offset)
        daily_count = 12 + (day_offset % 5) + (2 if business_day.weekday() >= 5 else 0)
        for sequence in range(daily_count):
            coffee_id = coffee[(day_offset + sequence * 2) % len(coffee)]
            line_ids = [coffee_id]
            if (sequence + day_offset) % 3 != 0:
                line_ids.append(food[(sequence + day_offset) % len(food)])
            if sequence % 7 == 0:
                line_ids.append(coffee[(day_offset + sequence + 1) % len(coffee)])
            lines: list[dict[str, object]] = []
            for line_index, product_id in enumerate(line_ids):
                product = product_by_id[product_id]
                quantity = 2 if (sequence + line_index) % 11 == 0 else 1
                discount = 30 if len(line_ids) > 1 and line_index == len(line_ids) - 1 and sequence % 5 == 0 else 0
                lines.append(
                    {
                        "product_id": product_id,
                        "quantity": quantity,
                        "unit_price": product["current_price"],
                        "unit_cost": product["current_cost"],
                        "discount": discount,
                    }
                )
            hour = 8 + (sequence * 11 % 12)
            minute = (sequence * 17 + day_offset * 3) % 60
            closed_at = datetime.combine(business_day, time(hour, minute), tzinfo=timezone(timedelta(hours=3)))
            receipts.append(
                {
                    "id": f"receipt-{business_day.isoformat()}-{sequence + 1:03d}",
                    "location_id": "lesnaya-14",
                    "closed_at": closed_at.isoformat(),
                    "lines": lines,
                }
            )
    return receipts


def write_json(name: str, payload: object) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / name).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    write_json(
        "cafe.json",
        {"id": "ugol", "name": "Угол × Лесная, 14", "currency": "RUB", "timezone": "Europe/Moscow"},
    )
    write_json("products.json", PRODUCTS)
    write_json("sales.json", build_receipts())
