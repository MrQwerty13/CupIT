from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from cupit.analytics.engine import dashboard_metrics, daily_metrics, product_metrics
from cupit.domain.models import Product, Receipt, SaleLine


def test_dashboard_uses_receipts_as_transactions_and_price_snapshots() -> None:
    receipts = (
        Receipt(
            id="r1",
            location_id="main",
            closed_at=datetime(2026, 8, 1, 10, tzinfo=timezone.utc),
            lines=(
                SaleLine("coffee", 2, Decimal("250"), Decimal("70"), Decimal("20")),
                SaleLine("cake", 1, Decimal("300"), Decimal("120")),
            ),
        ),
        Receipt(
            id="r2",
            location_id="main",
            closed_at=datetime(2026, 8, 1, 11, tzinfo=timezone.utc),
            lines=(SaleLine("coffee", 1, Decimal("250"), Decimal("70")),),
        ),
    )

    result = dashboard_metrics(receipts)

    assert result == {
        "revenue": 1030.0,
        "gross_profit": 700.0,
        "gross_margin": 67.96,
        "receipts": 2,
        "units_sold": 4,
        "average_receipt": 515.0,
    }


def test_product_metrics_include_products_without_sales() -> None:
    products = (
        Product("coffee", "Капучино", "Кофе", Decimal("250"), Decimal("70")),
        Product("tea", "Чай", "Чай", Decimal("200"), Decimal("40")),
    )
    receipts = (
        Receipt(
            id="r1",
            location_id="main",
            closed_at=datetime(2026, 8, 1, 10, tzinfo=timezone.utc),
            lines=(SaleLine("coffee", 2, Decimal("250"), Decimal("70")),),
        ),
    )

    result = product_metrics(receipts, products)

    assert result[0]["name"] == "Капучино"
    assert result[0]["units_sold"] == 2
    assert result[0]["gross_profit"] == 360.0
    assert result[0]["gross_margin"] == 72.0
    assert result[1]["name"] == "Чай"
    assert result[1]["units_sold"] == 0


def test_daily_metrics_use_cafe_timezone() -> None:
    receipts = (
        Receipt(
            id="late",
            location_id="main",
            closed_at=datetime(2026, 7, 31, 22, 30, tzinfo=timezone.utc),
            lines=(SaleLine("coffee", 1, Decimal("250"), Decimal("70")),),
        ),
    )

    result = daily_metrics(receipts, "Europe/Moscow")

    assert result[0]["date"] == "2026-08-01"
    assert result[0]["revenue"] == 250.0
