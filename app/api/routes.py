"""
CupIT - Coffee Shop Analytics Application
Flask API routes.

Endpoints:
GET /api/health
GET /api/dashboard
GET /api/products
GET /api/products/best-selling
GET /api/products/most-profitable
GET /api/sales/daily
GET /api/analytics
"""

from flask import Blueprint, jsonify, render_template
import logging

from app.services.analytics_service import AnalyticsService
from app.core.exceptions import handle_api_error


logger = logging.getLogger(__name__)

api = Blueprint('api', __name__, url_prefix='/api')


def init_routes(analytics_service: AnalyticsService):
    """Initialize routes with the analytics service."""
    
    @api.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({'status': 'healthy', 'service': 'cupit-api'})
    
    @api.route('/')
    def index():
        """Serve the dashboard UI."""
        return render_template('dashboard.html')
    
    @api.route('/dashboard')
    @handle_api_error
    def dashboard():
        """Get main dashboard metrics."""
        data = analytics_service.get_dashboard()
        return jsonify(data)
    
    @api.route('/products')
    @handle_api_error
    def products():
        """Get all products analysis."""
        data = analytics_service.get_product_analysis()
        return jsonify(data)
    
    @api.route('/products/best-selling')
    @handle_api_error
    def best_selling():
        """Get best-selling products."""
        data = analytics_service.get_product_analysis()
        return jsonify(data['best_selling'])
    
    @api.route('/products/most-profitable')
    @handle_api_error
    def most_profitable():
        """Get most profitable products."""
        data = analytics_service.get_profitability_analysis()
        return jsonify(data['most_profitable'])
    
    @api.route('/sales/daily')
    @handle_api_error
    def daily_sales():
        """Get daily sales data."""
        data = analytics_service.get_daily_analysis()
        return jsonify(data['daily_sales'])
    
    @api.route('/analytics')
    @handle_api_error
    def full_analytics():
        """Get complete analytics data."""
        data = analytics_service.get_full_analysis()
        return jsonify(data)
    
    return api