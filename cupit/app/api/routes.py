"""API routes for CupIT Flask application."""

import logging
from typing import Any, Dict

from flask import Blueprint, jsonify, request

from app.core.exceptions import (
    CupITException,
    DataFileNotFoundError,
    DataValidationError,
    OllamaUnavailableException,
)
from app.services.analytics_service import AnalyticsService
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__)

# These will be set during app initialization
analytics_service: AnalyticsService = None  # type: ignore
ai_service: AIService = None  # type: ignore


def init_routes(app_analytics_service: AnalyticsService, app_ai_service: AIService):
    """Initialize routes with service instances.
    
    Args:
        app_analytics_service: Analytics service instance.
        app_ai_service: AI service instance.
    """
    global analytics_service, ai_service
    analytics_service = app_analytics_service
    ai_service = app_ai_service


@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint.
    
    Returns:
        JSON with application status.
    """
    return jsonify({
        "status": "healthy",
        "service": "CupIT API"
    })


@api.route('/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard summary metrics.
    
    Returns:
        JSON with revenue, profit, transactions, units_sold, average_transaction.
    """
    try:
        data = analytics_service.get_dashboard()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        return jsonify({"error": "Failed to get dashboard data"}), 500


@api.route('/products', methods=['GET'])
def get_products():
    """Get all products.
    
    Returns:
        JSON list of products.
    """
    try:
        products = analytics_service.data_provider.get_products()
        result = [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "purchase_price": p.purchase_price,
                "selling_price": p.selling_price,
                "profit_per_unit": p.profit_per_unit,
                "profit_margin": p.profit_margin
            }
            for p in products
        ]
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        return jsonify({"error": "Failed to get products"}), 500


@api.route('/products/best-selling', methods=['GET'])
def get_best_selling():
    """Get best-selling products.
    
    Returns:
        JSON list of products ranked by units sold.
    """
    try:
        analysis = analytics_service.get_product_analysis()
        return jsonify(analysis["best_selling"])
    except Exception as e:
        logger.error(f"Error getting best-selling products: {e}")
        return jsonify({"error": "Failed to get best-selling products"}), 500


@api.route('/products/most-profitable', methods=['GET'])
def get_most_profitable():
    """Get most profitable products.
    
    Returns:
        JSON list of products ranked by total profit.
    """
    try:
        analysis = analytics_service.get_profitability_analysis()
        return jsonify(analysis["most_profitable"])
    except Exception as e:
        logger.error(f"Error getting most profitable products: {e}")
        return jsonify({"error": "Failed to get most profitable products"}), 500


@api.route('/products/least-selling', methods=['GET'])
def get_least_selling():
    """Get least-selling products.
    
    Returns:
        JSON list of products with lowest sales.
    """
    try:
        analysis = analytics_service.get_product_analysis()
        return jsonify(analysis["least_selling"])
    except Exception as e:
        logger.error(f"Error getting least-selling products: {e}")
        return jsonify({"error": "Failed to get least-selling products"}), 500


@api.route('/sales/daily', methods=['GET'])
def get_daily_sales():
    """Get daily sales analytics.
    
    Returns:
        JSON list of daily metrics.
    """
    try:
        analysis = analytics_service.get_daily_analysis()
        return jsonify(analysis["daily"])
    except Exception as e:
        logger.error(f"Error getting daily sales: {e}")
        return jsonify({"error": "Failed to get daily sales"}), 500


@api.route('/analytics', methods=['GET'])
def get_full_analytics():
    """Get complete analytics data.
    
    Returns:
        JSON with all analytics data.
    """
    try:
        data = analytics_service.get_full_analytics()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting full analytics: {e}")
        return jsonify({"error": "Failed to get analytics"}), 500


@api.route('/ai/analyze', methods=['POST'])
def ai_analyze():
    """Get AI-powered insights.
    
    Request:
        JSON with "question" field.
        
    Returns:
        JSON with AI answer.
    """
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Missing 'question' field"}), 400
        
        question = data['question']
        
        # Get structured analytics data
        analytics_data = analytics_service.get_full_analytics()
        
        # Send to AI service
        result = ai_service.analyze(analytics_data, question)
        return jsonify(result)
        
    except OllamaUnavailableException as e:
        logger.warning(f"Ollama unavailable: {e}")
        return jsonify({
            "error": "AI service unavailable",
            "message": str(e)
        }), 503
    except CupITException as e:
        logger.error(f"CupIT error in AI analyze: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error in AI analyze: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@api.errorhandler(DataFileNotFoundError)
def handle_data_file_not_found(error):
    """Handle data file not found errors."""
    return jsonify({"error": str(error)}), 404


@api.errorhandler(DataValidationError)
def handle_data_validation_error(error):
    """Handle data validation errors."""
    return jsonify({"error": str(error)}), 400


@api.errorhandler(CupITException)
def handle_cupit_exception(error):
    """Handle CupIT exceptions."""
    return jsonify({"error": str(error)}), 500
