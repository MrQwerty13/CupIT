"""Analytics orchestration independent from HTTP and JSON details."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from cupit.analytics.engine import dashboard_metrics, daily_metrics, filter_receipts, product_metrics
from cupit.data.interfaces import DataProvider


class AnalyticsService:
    def __init__(self, provider: DataProvider) -> None:
        self.provider = provider

    def _resolved_period(self, start: date | None, end: date | None) -> tuple[date, date]:
        cafe = self.provider.get_cafe()
        receipts = self.provider.get_receipts()
        if not receipts:
            today = date.today()
            return start or today, end or today
        from zoneinfo import ZoneInfo

        tz = ZoneInfo(cafe.timezone)
        dates = sorted(receipt.closed_at.astimezone(tz).date() for receipt in receipts)
        resolved_end = end or dates[-1]
        resolved_start = start or max(dates[0], resolved_end - timedelta(days=13))
        return resolved_start, resolved_end

    def _snapshot(self, start: date | None, end: date | None) -> dict[str, Any]:
        cafe = self.provider.get_cafe()
        products = self.provider.get_products()
        receipts = self.provider.get_receipts()
        resolved_start, resolved_end = self._resolved_period(start, end)
        selected = filter_receipts(receipts, cafe.timezone, resolved_start, resolved_end)
        return {
            "cafe": cafe,
            "products": products,
            "receipts": selected,
            "start": resolved_start,
            "end": resolved_end,
        }

    @staticmethod
    def _change(current: float | int, previous: float | int) -> float:
        if previous == 0:
            return 0.0 if current == 0 else 100.0
        return round((float(current) - float(previous)) / float(previous) * 100, 1)

    def get_dashboard(self, start: date | None = None, end: date | None = None) -> dict[str, Any]:
        snapshot = self._snapshot(start, end)
        cafe = snapshot["cafe"]
        receipts = snapshot["receipts"]
        metrics = dashboard_metrics(receipts)
        duration = (snapshot["end"] - snapshot["start"]).days + 1
        previous_end = snapshot["start"] - timedelta(days=1)
        previous_start = previous_end - timedelta(days=duration - 1)
        previous_receipts = filter_receipts(
            self.provider.get_receipts(), cafe.timezone, previous_start, previous_end
        )
        previous = dashboard_metrics(previous_receipts)
        changes = {
            key: self._change(metrics[key], previous[key])
            for key in ("revenue", "gross_profit", "average_receipt", "receipts")
        }
        daily = daily_metrics(receipts, cafe.timezone)
        products = product_metrics(receipts, snapshot["products"])
        best = products[0] if products else None
        focus = self._build_focus(metrics, products)
        return {
            "cafe": {
                "id": cafe.id,
                "name": cafe.name,
                "currency": cafe.currency,
                "timezone": cafe.timezone,
            },
            "period": {"from": snapshot["start"].isoformat(), "to": snapshot["end"].isoformat()},
            "metrics": metrics,
            "changes": changes,
            "daily": daily,
            "top_products": products[:5],
            "best_product": best,
            "focus": focus,
        }

    @staticmethod
    def _build_focus(metrics: dict[str, float | int], products: list[dict[str, Any]]) -> dict[str, str]:
        low_margin = [item for item in products if item["units_sold"] > 0 and item["gross_margin"] < 50]
        if low_margin:
            product = min(low_margin, key=lambda item: item["gross_margin"])
            return {
                "title": f"Проверьте маржу: {product['name']}",
                "body": f"Маржа товара составляет {product['gross_margin']:.1f}%. Проверьте себестоимость и цену перед следующим обновлением меню.",
            }
        return {
            "title": "Продажи растут устойчиво",
            "body": f"За выбранный период продано {metrics['units_sold']} позиций. Сфокусируйтесь на комбо с лидерами меню, чтобы увеличить средний чек.",
        }

    def get_daily_analysis(self, start: date | None = None, end: date | None = None) -> list[dict[str, Any]]:
        snapshot = self._snapshot(start, end)
        return daily_metrics(snapshot["receipts"], snapshot["cafe"].timezone)

    def get_product_performance(self, start: date | None = None, end: date | None = None) -> list[dict[str, Any]]:
        snapshot = self._snapshot(start, end)
        return product_metrics(snapshot["receipts"], snapshot["products"])

    def get_products(self) -> list[dict[str, Any]]:
        return [
            {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "current_price": float(product.current_price),
                "current_cost": float(product.current_cost),
                "active": product.active,
            }
            for product in self.provider.get_products()
        ]

    def get_full_analysis(self, start: date | None = None, end: date | None = None) -> dict[str, Any]:
        dashboard = self.get_dashboard(start, end)
        dashboard["products"] = self.get_product_performance(start, end)
        return dashboard

    def get_ai_context(self, start: date | None = None, end: date | None = None) -> dict[str, Any]:
        dashboard = self.get_dashboard(start, end)
        return {
            "period": dashboard["period"],
            "currency": dashboard["cafe"]["currency"],
            "metrics": dashboard["metrics"],
            "daily": dashboard["daily"],
            "top_products": dashboard["top_products"],
        }
