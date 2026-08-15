"""Deterministic and source-independent analytics calculations."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

from cupit.domain.models import Product, Receipt

MONEY_STEP = Decimal("0.01")


def _money(value: Decimal) -> float:
    return float(value.quantize(MONEY_STEP, rounding=ROUND_HALF_UP))


def filter_receipts(
    receipts: tuple[Receipt, ...],
    timezone: str,
    start: date | None,
    end: date | None,
) -> tuple[Receipt, ...]:
    tz = ZoneInfo(timezone)
    return tuple(
        receipt
        for receipt in receipts
        if (start is None or receipt.closed_at.astimezone(tz).date() >= start)
        and (end is None or receipt.closed_at.astimezone(tz).date() <= end)
    )


def dashboard_metrics(receipts: tuple[Receipt, ...]) -> dict[str, float | int]:
    revenue = sum((line.revenue for receipt in receipts for line in receipt.lines), Decimal("0"))
    gross_profit = sum(
        (line.gross_profit for receipt in receipts for line in receipt.lines),
        Decimal("0"),
    )
    units = sum(line.quantity for receipt in receipts for line in receipt.lines)
    receipt_count = len(receipts)
    average_receipt = revenue / receipt_count if receipt_count else Decimal("0")
    margin = gross_profit / revenue * 100 if revenue else Decimal("0")
    return {
        "revenue": _money(revenue),
        "gross_profit": _money(gross_profit),
        "gross_margin": _money(margin),
        "receipts": receipt_count,
        "units_sold": units,
        "average_receipt": _money(average_receipt),
    }


def daily_metrics(receipts: tuple[Receipt, ...], timezone: str) -> list[dict[str, float | int | str]]:
    tz = ZoneInfo(timezone)
    groups: dict[date, list[Receipt]] = defaultdict(list)
    for receipt in receipts:
        groups[receipt.closed_at.astimezone(tz).date()].append(receipt)
    result: list[dict[str, float | int | str]] = []
    for day in sorted(groups):
        metrics = dashboard_metrics(tuple(groups[day]))
        result.append({"date": day.isoformat(), **metrics})
    return result


def product_metrics(
    receipts: tuple[Receipt, ...],
    products: tuple[Product, ...],
) -> list[dict[str, float | int | str | bool]]:
    totals: dict[str, dict[str, Decimal | int]] = {
        product.id: {"units": 0, "revenue": Decimal("0"), "profit": Decimal("0")}
        for product in products
    }
    for receipt in receipts:
        for line in receipt.lines:
            bucket = totals[line.product_id]
            bucket["units"] = int(bucket["units"]) + line.quantity
            bucket["revenue"] = Decimal(bucket["revenue"]) + line.revenue
            bucket["profit"] = Decimal(bucket["profit"]) + line.gross_profit

    result: list[dict[str, float | int | str | bool]] = []
    for product in products:
        bucket = totals[product.id]
        revenue = Decimal(bucket["revenue"])
        profit = Decimal(bucket["profit"])
        result.append(
            {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "active": product.active,
                "units_sold": int(bucket["units"]),
                "revenue": _money(revenue),
                "gross_profit": _money(profit),
                "gross_margin": _money(profit / revenue * 100 if revenue else Decimal("0")),
            }
        )
    return sorted(result, key=lambda item: (-float(item["revenue"]), str(item["name"])))
