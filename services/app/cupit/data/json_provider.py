"""JSON implementation of the normalized DataProvider contract."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from cupit.core.exceptions import DataSourceError, DataValidationError
from cupit.data.interfaces import DataProvider
from cupit.domain.models import Cafe, Product, Receipt, SaleLine


class JsonDataProvider(DataProvider):
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir

    def _read(self, filename: str) -> Any:
        path = self.data_dir / filename
        try:
            with path.open(encoding="utf-8") as source:
                return json.load(source)
        except FileNotFoundError as exc:
            raise DataSourceError(f"Data file is missing: {path}", "DATA_FILE_MISSING") from exc
        except json.JSONDecodeError as exc:
            raise DataSourceError(
                f"Malformed JSON in {path.name} at line {exc.lineno}",
                "MALFORMED_JSON",
            ) from exc
        except OSError as exc:
            raise DataSourceError(f"Unable to read data file: {path}") from exc

    @staticmethod
    def _money(value: Any, field: str) -> Decimal:
        try:
            result = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise DataValidationError(f"{field} must be a valid number") from exc
        if result < 0:
            raise DataValidationError(f"{field} must not be negative")
        return result

    def get_cafe(self) -> Cafe:
        raw = self._read("cafe.json")
        if not isinstance(raw, dict):
            raise DataValidationError("cafe.json must contain an object")
        try:
            return Cafe(
                id=str(raw["id"]),
                name=str(raw["name"]),
                currency=str(raw["currency"]),
                timezone=str(raw["timezone"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise DataValidationError("Invalid cafe structure") from exc

    def get_products(self) -> tuple[Product, ...]:
        raw = self._read("products.json")
        if not isinstance(raw, list):
            raise DataValidationError("products.json must contain an array")
        products: list[Product] = []
        seen: set[str] = set()
        for index, item in enumerate(raw):
            if not isinstance(item, dict):
                raise DataValidationError("Invalid product structure", {"index": index})
            try:
                product_id = str(item["id"])
                if product_id in seen:
                    raise DataValidationError("Duplicate product id", {"id": product_id})
                seen.add(product_id)
                products.append(
                    Product(
                        id=product_id,
                        name=str(item["name"]),
                        category=str(item["category"]),
                        current_price=self._money(item["current_price"], "current_price"),
                        current_cost=self._money(item["current_cost"], "current_cost"),
                        active=bool(item.get("active", True)),
                    )
                )
            except KeyError as exc:
                raise DataValidationError("Invalid product structure", {"index": index}) from exc
        return tuple(products)

    def get_receipts(self) -> tuple[Receipt, ...]:
        raw = self._read("sales.json")
        if not isinstance(raw, list):
            raise DataValidationError("sales.json must contain an array")
        products = {product.id: product for product in self.get_products()}
        receipts: list[Receipt] = []
        seen: set[str] = set()
        for receipt_index, item in enumerate(raw):
            if not isinstance(item, dict):
                raise DataValidationError("Invalid receipt structure", {"index": receipt_index})
            try:
                receipt_id = str(item["id"])
                if receipt_id in seen:
                    raise DataValidationError("Duplicate receipt id", {"id": receipt_id})
                seen.add(receipt_id)
                closed_at = datetime.fromisoformat(str(item["closed_at"]).replace("Z", "+00:00"))
                if closed_at.tzinfo is None:
                    raise ValueError("timezone is required")
                raw_lines = item["lines"]
                if not isinstance(raw_lines, list) or not raw_lines:
                    raise ValueError("lines must be a non-empty array")
                lines: list[SaleLine] = []
                for line_index, line in enumerate(raw_lines):
                    if not isinstance(line, dict):
                        raise ValueError(f"line {line_index} must be an object")
                    product_id = str(line["product_id"])
                    product = products.get(product_id)
                    if product is None:
                        raise DataValidationError(
                            "Receipt references an unknown product",
                            {"receipt_id": receipt_id, "product_id": product_id},
                        )
                    lines.append(
                        SaleLine(
                            product_id=product_id,
                            quantity=int(line["quantity"]),
                            unit_price=self._money(line.get("unit_price", product.current_price), "unit_price"),
                            unit_cost=self._money(line.get("unit_cost", product.current_cost), "unit_cost"),
                            discount=self._money(line.get("discount", 0), "discount"),
                        )
                    )
                receipts.append(
                    Receipt(
                        id=receipt_id,
                        location_id=str(item.get("location_id", "main")),
                        closed_at=closed_at,
                        lines=tuple(lines),
                    )
                )
            except DataValidationError:
                raise
            except (KeyError, TypeError, ValueError) as exc:
                raise DataValidationError(
                    "Invalid receipt structure",
                    {"index": receipt_index, "reason": str(exc)},
                ) from exc
        return tuple(receipts)
