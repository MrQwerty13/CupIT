from __future__ import annotations

import json
from pathlib import Path

from cupit.core.config import Settings
from cupit.data.json_provider import JsonDataProvider
from scripts.dataset_manager import create_template, import_dataset


def bundle() -> dict[str, object]:
    return {
        "cafe": {
            "id": "test-cafe",
            "name": "Тестовое кафе",
            "currency": "RUB",
            "timezone": "Europe/Moscow",
        },
        "products": [
            {
                "id": "coffee",
                "name": "Кофе",
                "category": "Кофе",
                "current_price": 250,
                "current_cost": 70,
                "active": True,
            }
        ],
        "sales": [
            {
                "id": "receipt-1",
                "location_id": "main",
                "closed_at": "2026-08-15T10:00:00+03:00",
                "lines": [
                    {
                        "product_id": "coffee",
                        "quantity": 2,
                        "unit_price": 250,
                        "unit_cost": 70,
                        "discount": 0,
                    }
                ],
            }
        ],
    }


def test_import_bundle_validates_versions_and_activates(tmp_path: Path) -> None:
    source = tmp_path / "incoming.json"
    source.write_text(json.dumps(bundle(), ensure_ascii=False), encoding="utf-8")
    data_root = tmp_path / "data"

    result = import_dataset(source, data_root)

    active_relative = (data_root / "ACTIVE_DATASET").read_text(encoding="utf-8").strip()
    active = data_root / active_relative
    assert active.is_dir()
    assert result["receipts"] == 1
    assert result["sale_lines"] == 1
    assert result["sha256"]
    assert JsonDataProvider(active).get_receipts()[0].lines[0].quantity == 2
    assert json.loads((active / "manifest.json").read_text(encoding="utf-8"))["active"] is True


def test_template_uses_existing_catalog(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    payload = bundle()
    (catalog / "cafe.json").write_text(json.dumps(payload["cafe"]), encoding="utf-8")
    (catalog / "products.json").write_text(json.dumps(payload["products"]), encoding="utf-8")
    output = tmp_path / "template.json"

    result = create_template(output, catalog)

    template = json.loads(output.read_text(encoding="utf-8"))
    assert result["products"] == 1
    assert template["sales"][0]["lines"][0]["product_id"] == "coffee"


def test_settings_resolve_active_dataset(monkeypatch, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    active = tmp_path / "imports" / "batch-1"
    active.mkdir(parents=True)
    (tmp_path / "ACTIVE_DATASET").write_text("imports/batch-1\n", encoding="utf-8")
    monkeypatch.setenv("CUPIT_DATA_ROOT", str(tmp_path))
    monkeypatch.delenv("CUPIT_DATA_DIR", raising=False)

    settings = Settings.from_env()

    assert settings.data_dir == active
