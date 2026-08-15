from __future__ import annotations

from pathlib import Path

from cupit import create_app
from cupit.core.config import Settings


ROOT = Path(__file__).resolve().parents[1]


def make_client():  # type: ignore[no-untyped-def]
    app = create_app(
        Settings(
            data_dir=ROOT / "data" / "samples",
            ollama_host="http://127.0.0.1:1",
            ollama_timeout_seconds=0.1,
        )
    )
    app.testing = True
    return app.test_client()


def test_health_does_not_depend_on_ollama() -> None:
    response = make_client().get("/api/v1/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_dashboard_returns_real_sample_metrics() -> None:
    response = make_client().get("/api/v1/dashboard")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["metrics"]["revenue"] > 0
    assert payload["metrics"]["receipts"] > 100
    assert len(payload["daily"]) == 14
    assert payload["top_products"]


def test_invalid_period_returns_json_error() -> None:
    response = make_client().get("/api/v1/dashboard?from=wrong")

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "INVALID_REQUEST"


def test_ai_unavailable_does_not_crash_api() -> None:
    response = make_client().post(
        "/api/v1/ai/insights",
        json={"question": "Что улучшить?"},
    )

    assert response.status_code == 503
    assert response.get_json()["error"]["code"] == "AI_UNAVAILABLE"
