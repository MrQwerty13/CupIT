"""Versioned public API routes."""

from __future__ import annotations

from datetime import date

from flask import Blueprint, jsonify, request

from cupit.core.exceptions import InvalidRequestError
from cupit.services.ai_service import AiService
from cupit.services.analytics_service import AnalyticsService


def _parse_date(value: str | None, field: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InvalidRequestError(f"{field} must use YYYY-MM-DD format") from exc


def _period() -> tuple[date | None, date | None]:
    start = _parse_date(request.args.get("from"), "from")
    end = _parse_date(request.args.get("to"), "to")
    if start and end and start > end:
        raise InvalidRequestError("from must be earlier than or equal to to")
    return start, end


def create_api_blueprint(
    analytics: AnalyticsService,
    ai: AiService,
) -> Blueprint:
    api = Blueprint("api_v1", __name__, url_prefix="/api/v1")

    @api.route("/health", methods=["GET"])
    def health():  # type: ignore[no-untyped-def]
        return jsonify({"status": "ok", "service": "cupit-api", "version": "0.1.0"})

    @api.route("/dashboard", methods=["GET"])
    def dashboard():  # type: ignore[no-untyped-def]
        start, end = _period()
        return jsonify(analytics.get_dashboard(start, end))

    @api.route("/analytics", methods=["GET"])
    def analytics_snapshot():  # type: ignore[no-untyped-def]
        start, end = _period()
        return jsonify(analytics.get_full_analysis(start, end))

    @api.route("/products", methods=["GET"])
    def products():  # type: ignore[no-untyped-def]
        return jsonify({"items": analytics.get_products()})

    @api.route("/products/performance", methods=["GET"])
    def product_performance():  # type: ignore[no-untyped-def]
        start, end = _period()
        return jsonify({"items": analytics.get_product_performance(start, end)})

    @api.route("/sales/daily", methods=["GET"])
    def daily_sales():  # type: ignore[no-untyped-def]
        start, end = _period()
        return jsonify({"items": analytics.get_daily_analysis(start, end)})

    @api.route("/ai/insights", methods=["POST", "OPTIONS"])
    def ai_insights():  # type: ignore[no-untyped-def]
        if request.method == "OPTIONS":
            return "", 204
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            raise InvalidRequestError("Request body must be a JSON object")
        question = payload.get("question")
        if not isinstance(question, str) or not question.strip():
            raise InvalidRequestError("question is required")
        if len(question) > 1000:
            raise InvalidRequestError("question must not exceed 1000 characters")
        start = _parse_date(payload.get("from"), "from")
        end = _parse_date(payload.get("to"), "to")
        if start and end and start > end:
            raise InvalidRequestError("from must be earlier than or equal to to")
        context = analytics.get_ai_context(start, end)
        answer = ai.analyze(question.strip(), context)
        return jsonify(
            {
                "answer": answer,
                "model": ai.model,
                "prompt_version": ai.prompt_version,
                "source": "structured_analytics",
            }
        )

    return api
