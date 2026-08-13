"""Main Flask application module."""

import logging
import sys
from pathlib import Path

from flask import Flask

from app.api.routes import api, init_routes
from app.core.config import Config
from app.data.json_provider import JsonDataProvider
from app.services.analytics_service import AnalyticsService
from app.services.ai_service import AIService


def setup_logging(debug: bool = False):
    """Configure application logging."""
    level = logging.DEBUG if debug else logging.INFO
    format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=level,
        format=format_str,
        stream=sys.stdout
    )
    
    # Set third-party loggers to WARNING
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def create_app(config: Config = None) -> Flask:
    """Create and configure the Flask application.
    
    Args:
        config: Application configuration. If None, loads from environment.
        
    Returns:
        Configured Flask application instance.
    """
    if config is None:
        config = Config()
    
    # Setup logging
    setup_logging(config.DEBUG)
    logger = logging.getLogger(__name__)
    logger.info("Starting CupIT application")
    
    # Create Flask app
    app = Flask(__name__)
    app.config['DEBUG'] = config.DEBUG
    
    # Initialize data provider
    logger.info(f"Initializing JsonDataProvider with data directory: {config.DATA_DIR}")
    data_provider = JsonDataProvider(config.DATA_DIR)
    
    # Initialize services
    analytics_service = AnalyticsService(data_provider)
    ai_service = AIService(config)
    
    # Initialize routes with services
    init_routes(analytics_service, ai_service)
    
    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')
    
    logger.info("CupIT application initialized successfully")
    
    return app


def main():
    """Run the Flask application."""
    config = Config()
    app = create_app(config)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting Flask server on {config.API_HOST}:{config.API_PORT}")
    
    app.run(
        host=config.API_HOST,
        port=config.API_PORT,
        debug=config.DEBUG
    )


if __name__ == '__main__':
    main()
