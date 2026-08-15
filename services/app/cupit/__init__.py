"""CupIT application package."""

from __future__ import annotations

import logging

from flask import Flask, jsonify, request

from cupit.api.routes import create_api_blueprint
from cupit.core.config import Settings
from cupit.core.exceptions import CupitError
from cupit.data.json_provider import JsonDataProvider
from cupit.services.ai_service import AiService
from cupit.services.analytics_service import AnalyticsService


def create_app(settings: Settings | None = None) -> Flask:
    """Create the Flask application and wire infrastructure dependencies."""

    app = Flask(__name__)
    app_settings = settings or Settings.from_env()
    provider = JsonDataProvider(app_settings.data_dir)
    analytics_service = AnalyticsService(provider)
    ai_service = AiService(
        host=app_settings.ollama_host,
        model=app_settings.ollama_model,
        timeout_seconds=app_settings.ollama_timeout_seconds,
        temperature=app_settings.ollama_temperature,
        max_tokens=app_settings.ollama_max_tokens,
    )

    logging.basicConfig(
        level=getattr(logging, app_settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    app.logger.info("Starting CupIT API with data directory %s", app_settings.data_dir)
    app.register_blueprint(create_api_blueprint(analytics_service, ai_service))

    @app.after_request
    def add_response_headers(response):  # type: ignore[no-untyped-def]
        response.headers["Access-Control-Allow-Origin"] = app_settings.cors_origin
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Request-ID"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.before_request
    def log_request() -> None:
        if request.method != "OPTIONS":
            app.logger.info("%s %s", request.method, request.path)

    @app.errorhandler(CupitError)
    def handle_cupit_error(error: CupitError):  # type: ignore[no-untyped-def]
        return jsonify({"error": error.to_dict()}), error.status_code

    @app.errorhandler(404)
    def handle_not_found(_error):  # type: ignore[no-untyped-def]
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Endpoint not found"}}), 404

    return app


__all__ = ["create_app"]
