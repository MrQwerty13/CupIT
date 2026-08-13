"""Analytics service.

This service orchestrates the analytics engine.
The API communicates with this service layer rather than
directly calling individual analytics functions.

Architecture:
    API → AnalyticsService → Analytics modules → DataProvider
"""

import logging
from typing import Any, Dict, List

from app.analytics import dates, products, profitability, sales
from app.data.interfaces import DataProvider
from app.models import Product, Sale

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service layer for analytics operations.
    
    This class orchestrates calls to various analytics modules
    and provides a unified interface for the API layer.
    """
    
    def __init__(self, data_provider: DataProvider):
        """Initialize analytics service.
        
        Args:
            data_provider: Data provider instance for fetching data.
        """
        self.data_provider = data_provider
        logger.info("AnalyticsService initialized")
    
    def _get_data(self):
        """Fetch data from the data provider.
        
        Returns:
            Tuple of (products, sales).
        """
        products = self.data_provider.get_products()
        sales = self.data_provider.get_sales()
        return products, sales
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get dashboard summary metrics.
        
        Returns:
            Dictionary with key metrics for dashboard.
        """
        products, sales = self._get_data()
        
        revenue = sales.calculate_total_revenue(sales, products)
        units_sold = sales.calculate_total_units(sales)
        transactions = sales.calculate_transaction_count(sales)
        avg_transaction = sales.calculate_average_transaction_value(sales, products)
        
        # Calculate total profit
        product_map = {p.id: p for p in products}
        total_profit = 0.0
        for sale in sales:
            product = product_map.get(sale.product_id)
            if product:
                total_profit += product.profit_per_unit * sale.quantity
        
        return {
            "revenue": round(revenue, 2),
            "profit": round(total_profit, 2),
            "transactions": transactions,
            "units_sold": units_sold,
            "average_transaction": round(avg_transaction, 2)
        }
    
    def get_product_analysis(self) -> Dict[str, Any]:
        """Get product analysis including best/worst sellers.
        
        Returns:
            Dictionary with product rankings.
        """
        products, sales = self._get_data()
        
        return {
            "best_selling": products.get_best_selling_products(sales, products),
            "highest_revenue": products.get_highest_revenue_products(sales, products),
            "least_selling": products.get_least_selling_products(sales, products)
        }
    
    def get_profitability_analysis(self) -> Dict[str, Any]:
        """Get profitability analysis.
        
        Returns:
            Dictionary with profitability rankings.
        """
        products, sales = self._get_data()
        
        return {
            "most_profitable": profitability.get_most_profitable_products(
                sales, products, by="total_profit"
            ),
            "highest_margin": profitability.get_most_profitable_products(
                sales, products, by="profit_margin"
            ),
            "least_profitable": profitability.get_least_profitable_products(
                sales, products, by="total_profit"
            )
        }
    
    def get_daily_analysis(self) -> Dict[str, Any]:
        """Get daily analysis.
        
        Returns:
            Dictionary with daily metrics.
        """
        products, sales = self._get_data()
        
        return {
            "daily": dates.calculate_daily_analytics(sales, products)
        }
    
    def get_full_analytics(self) -> Dict[str, Any]:
        """Get complete analytics data for AI or comprehensive reports.
        
        Returns:
            Dictionary with all analytics data.
        """
        products, sales = self._get_data()
        
        # Dashboard metrics
        revenue = sales.calculate_total_revenue(sales, products)
        units_sold = sales.calculate_total_units(sales)
        transactions = sales.calculate_transaction_count(sales)
        
        product_map = {p.id: p for p in products}
        total_profit = 0.0
        for sale in sales:
            product = product_map.get(sale.product_id)
            if product:
                total_profit += product.profit_per_unit * sale.quantity
        
        # Category breakdown
        category_revenue = sales.calculate_sales_by_category(sales, products)
        
        return {
            "summary": {
                "revenue": round(revenue, 2),
                "profit": round(total_profit, 2),
                "transactions": transactions,
                "units_sold": units_sold
            },
            "best_products": products.get_best_selling_products(sales, products, limit=5),
            "worst_products": products.get_least_selling_products(sales, products, limit=5),
            "most_profitable": profitability.get_most_profitable_products(
                sales, products, limit=5, by="total_profit"
            ),
            "category_breakdown": category_revenue,
            "daily_sales": dates.calculate_daily_analytics(sales, products)
        }
