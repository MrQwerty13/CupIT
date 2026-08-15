"""Prepare, validate and activate datasets for CupIT analytics.

Usage:
    python scripts/dataset_manager.py template ./cupit-data.json
    python scripts/dataset_manager.py import ./cupit-data.json
    python scripts/dataset_manager.py import ./sales.json --catalog ./data/samples
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Sequence
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "services" / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from cupit.core.exceptions import CupitError  # noqa: E402
from cupit.data.json_provider import JsonDataProvider  # noqa: E402


REQUIRED_FILES = ("cafe.json", "products.json", "sales.json")


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Файл не найден: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Некорректный JSON в {path}: строка {exc.lineno}") from exc
    except OSError as exc:
        raise ValueError(f"Не удалось прочитать файл: {path}") from exc


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _default_catalog(data_root: Path) -> Path:
    pointer = data_root / "ACTIVE_DATASET"
    if pointer.is_file():
        relative = pointer.read_text(encoding="utf-8").strip()
        candidate = (data_root / relative).resolve()
        if candidate.is_relative_to(data_root.resolve()) and candidate.is_dir():
            return candidate
    return data_root / "samples"


def create_template(output: Path, catalog: Path) -> dict[str, Any]:
    """Create a single editable bundle with cafe, products and one sale example."""

    if output.exists():
        raise ValueError(f"Файл уже существует: {output}")
    cafe = _read_json(catalog / "cafe.json")
    products = _read_json(catalog / "products.json")
    if not isinstance(products, list) or not products:
        raise ValueError("Каталог должен содержать хотя бы один товар")
    product = products[0]
    template = {
        "cafe": cafe,
        "products": products,
        "sales": [
            {
                "id": "receipt-001",
                "location_id": "main",
                "closed_at": "2026-08-15T10:30:00+03:00",
                "lines": [
                    {
                        "product_id": product["id"],
                        "quantity": 1,
                        "unit_price": product["current_price"],
                        "unit_cost": product["current_cost"],
                        "discount": 0,
                    }
                ],
            }
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    _write_json(output, template)
    return {"template": str(output.resolve()), "products": len(products)}


def _stage_source(source: Path, catalog: Path, staging: Path) -> None:
    if source.is_dir():
        for filename in REQUIRED_FILES:
            source_file = source / filename
            if not source_file.is_file():
                raise ValueError(f"В каталоге отсутствует {filename}")
            shutil.copy2(source_file, staging / filename)
        return

    payload = _read_json(source)
    if isinstance(payload, dict) and {"cafe", "products", "sales"}.issubset(payload):
        _write_json(staging / "cafe.json", payload["cafe"])
        _write_json(staging / "products.json", payload["products"])
        _write_json(staging / "sales.json", payload["sales"])
        return

    if isinstance(payload, list):
        for filename in ("cafe.json", "products.json"):
            catalog_file = catalog / filename
            if not catalog_file.is_file():
                raise ValueError(f"Каталог не содержит {filename}")
            shutil.copy2(catalog_file, staging / filename)
        _write_json(staging / "sales.json", payload)
        return

    raise ValueError(
        "Ожидается каталог с тремя JSON-файлами, bundle с ключами "
        "cafe/products/sales или список чеков"
    )


def _dataset_digest(dataset_dir: Path) -> str:
    digest = hashlib.sha256()
    for filename in REQUIRED_FILES:
        digest.update(filename.encode("utf-8"))
        digest.update((dataset_dir / filename).read_bytes())
    return digest.hexdigest()


def _activate(data_root: Path, relative_dataset: Path) -> None:
    pointer = data_root / "ACTIVE_DATASET"
    temporary = data_root / f".ACTIVE_DATASET.{uuid4().hex}.tmp"
    temporary.write_text(relative_dataset.as_posix() + "\n", encoding="utf-8")
    os.replace(temporary, pointer)


def import_dataset(
    source: Path,
    data_root: Path,
    catalog: Path | None = None,
    activate: bool = True,
) -> dict[str, Any]:
    """Validate a source, persist an immutable import and optionally activate it."""

    data_root.mkdir(parents=True, exist_ok=True)
    catalog_dir = catalog or _default_catalog(data_root)
    staging_root = data_root / ".staging"
    staging_root.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="cupit-", dir=staging_root) as temporary:
        staging = Path(temporary)
        _stage_source(source.resolve(), catalog_dir.resolve(), staging)
        provider = JsonDataProvider(staging)
        cafe = provider.get_cafe()
        products = provider.get_products()
        receipts = provider.get_receipts()
        digest = _dataset_digest(staging)
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        batch_name = f"{timestamp}-{digest[:10]}"
        relative = Path("imports") / batch_name
        destination = data_root / relative

        if destination.exists():
            raise ValueError(f"Партия уже существует: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(staging, destination)
        manifest = {
            "batch_id": batch_name,
            "imported_at": datetime.now(UTC).isoformat(),
            "source": str(source.resolve()),
            "sha256": digest,
            "cafe_id": cafe.id,
            "products": len(products),
            "receipts": len(receipts),
            "sale_lines": sum(len(receipt.lines) for receipt in receipts),
            "active": activate,
        }
        _write_json(destination / "manifest.json", manifest)

    if activate:
        _activate(data_root, relative)
    return {**manifest, "dataset_dir": str(destination.resolve())}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Подготовка и перенос данных в CupIT для аналитики",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=ROOT / "data",
        help="Корневой каталог данных CupIT (по умолчанию: ./data)",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    template = commands.add_parser("template", help="Создать JSON-шаблон для заполнения")
    template.add_argument("output", type=Path, help="Путь нового bundle JSON")
    template.add_argument("--catalog", type=Path, help="Каталог товаров для шаблона")

    importer = commands.add_parser("import", help="Проверить и перенести заполненные данные")
    importer.add_argument("source", type=Path, help="Bundle JSON, sales JSON или каталог")
    importer.add_argument("--catalog", type=Path, help="Каталог cafe/products для sales JSON")
    importer.add_argument(
        "--no-activate",
        action="store_true",
        help="Сохранить партию, не делая её активной",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "template":
            catalog = args.catalog or _default_catalog(args.data_root)
            result = create_template(args.output, catalog)
        else:
            result = import_dataset(
                source=args.source,
                data_root=args.data_root,
                catalog=args.catalog,
                activate=not args.no_activate,
            )
    except (ValueError, CupitError) as exc:
        message = exc.message if isinstance(exc, CupitError) else str(exc)
        print(json.dumps({"status": "error", "message": message}, ensure_ascii=False), file=sys.stderr)
        return 1

    print(json.dumps({"status": "ok", **result}, ensure_ascii=False, indent=2))
    if args.command == "import" and not args.no_activate:
        print("Набор активирован. Перезапустите CupIT API, чтобы применить его.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
