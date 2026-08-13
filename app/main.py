"""
CupIT - Coffee Shop Analytics Application
Main Flask application entry point.

Data Flow:
JSON → DataProvider → Models → Analytics → Service → API → UI/AI
"""

import logging
from flask import Flask
from app.core.config import Config
from app.data.interfaces import JsonDataProvider
from app.services.analytics_service import AnalyticsService
from app.api.routes import init_routes


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    """Create and configure the Flask application."""
    
    logger.info("Creating CupIT application")
    
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['DEBUG'] = Config.DEBUG
    
    # Initialize data provider
    logger.info(f"Initializing data provider with directory: {Config.get_data_dir()}")
    data_provider = JsonDataProvider(Config.get_data_dir())
    
    # Initialize analytics service
    analytics_service = AnalyticsService(data_provider)
    
    # Register routes
    logger.info("Registering API routes")
    api_blueprint = init_routes(analytics_service)
    app.register_blueprint(api_blueprint)
    
    logger.info("CupIT application created successfully")
    
    return app


if __name__ == '__main__':
    app = create_app()
    logger.info(f"Starting server on {Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)