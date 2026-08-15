from __future__ import annotations

import json
from pathlib import Path

import pytest

from cupit.core.exceptions import DataSourceError, DataValidationError
from cupit.data.json_provider import JsonDataProvider


ROOT = Path(__file__).resolve().parents[1]


def test_sample_json_loads_normalized_models() -> None:
    provider = JsonDataProvider(ROOT / "data" / "samples")

    assert provider.get_cafe().currency == "RUB"
    assert len(provider.get_products()) == 10
    assert len(provider.get_receipts()) > 100
    assert all(receipt.closed_at.tzinfo is not None for receipt in provider.get_receipts())


def test_missing_file_has_stable_error(tmp_path: Path) -> None:
    provider = JsonDataProvider(tmp_path)

    with pytest.raises(DataSourceError) as error:
        provider.get_cafe()

    assert error.value.code == "DATA_FILE_MISSING"


def test_malformed_json_has_stable_error(tmp_path: Path) -> None:
    (tmp_path / "cafe.json").write_text("{", encoding="utf-8")

    with pytest.raises(DataSourceError) as error:
        JsonDataProvider(tmp_path).get_cafe()

    assert error.value.code == "MALFORMED_JSON"


def test_unknown_product_reference_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "products.json").write_text("[]", encoding="utf-8")
    (tmp_path / "sales.json").write_text(
        json.dumps(
            [
                {
                    "id": "r1",
                    "closed_at": "2026-08-01T10:00:00+03:00",
                    "lines": [{"product_id": "missing", "quantity": 1, "unit_price": 10, "unit_cost": 5}],
                }
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(DataValidationError) as error:
        JsonDataProvider(tmp_path).get_receipts()

    assert error.value.details["product_id"] == "missing"


def test_duplicate_product_is_rejected(tmp_path: Path) -> None:
    product = {
        "id": "coffee",
        "name": "Кофе",
        "category": "Кофе",
        "current_price": 250,
        "current_cost": 70,
    }
    (tmp_path / "products.json").write_text(
        json.dumps([product, product]),
        encoding="utf-8",
    )

    with pytest.raises(DataValidationError) as error:
        JsonDataProvider(tmp_path).get_products()

    assert error.value.message == "Duplicate product id"
