"""
CupIT - Coffee Shop Analytics Application
Analytics service that orchestrates the analytics engine.

The API should communicate with the service layer rather than 
directly calling individual analytics functions.

Architecture:
API → AnalyticsService → Analytics modules → DataProvider
"""

import logging

from app.data.interfaces import DataProvider
from app import analytics


logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service layer for analytics operations.
    
    Orchestrates the analytics engine and provides high-level methods
    for the API to use.
    """
    
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider
        logger.info("AnalyticsService initialized")
    
    def _get_products_dict(self) -> dict[int, any]:
        """Get products as a dictionary keyed by product ID."""
        products = self.data_provider.get_products()
        return {p.id: p for p in products}
    
    def get_dashboard(self) -> dict:
        """
        Get main dashboard metrics.
        
        Returns:
            dict with revenue, profit, transactions, units_sold, average_transaction
        """
        logger.debug("Getting dashboard data")
        
        sales = self.data_provider.get_sales()
        products = self._get_products_dict()
        
        revenue = analytics.calculate_total_revenue(sales, products)
        profit = analytics.calculate_total_profit(sales, products)
        transactions = analytics.calculate_transaction_count(sales)
        units_sold = analytics.calculate_total_units(sales)
        avg_transaction = analytics.calculate_average_transaction_value(sales, products)
        
        return {
            'revenue': round(revenue, 2),
            'profit': round(profit, 2),
            'transactions': transactions,
            'units_sold': units_sold,
            'average_transaction': round(avg_transaction, 2)
        }
    
    def get_product_analysis(self) -> dict:
        """
        Get product analysis including best-selling, highest-revenue, and least-selling.
        
        Returns:
            dict with best_selling, highest_revenue, leastselling lists
        """
        logger.debug("Getting product analysis")
        
        sales = self.data_provider.get_sales()
        products = self._get_products_dict()
        
        return {
            'best_selling': analytics.get_best_selling_products(sales, products),
            'highest_revenue': analytics.get_highest_revenue_products(sales, products),
            'least_selling': analytics.get_lowest_selling_products(sales, products)
        }
    
    def get_profitability_analysis(self) -> dict:
        """
        Get profitability analysis.
        
        Returns:
            dict with most_profitable products list
        """
        logger.debug("Getting profitability analysis")
        
        sales = self.data_provider.get_sales()
        products = self._get_products_dict()
        
        return {
            'most_profitable': analytics.get_most_profitable_products(sales, products)
        }
    
    def get_daily_analysis(self) -> dict:
        """
        Get daily sales analysis.
        
        Returns:
            dict with daily_sales list
        """
        logger.debug("Getting daily analysis")
        
        sales = self.data_provider.get_sales()
        products = self._get_products_dict()
        
        return {
            'daily_sales': analytics.get_sales_by_day(sales, products)
        }
    
    def get_category_analysis(self) -> dict:
        """
        Get category-based analysis.
        
        Returns:
            dict with sales_by_category
        """
        logger.debug("Getting category analysis")
        
        sales = self.data_provider.get_sales()
        products = self._get_products_dict()
        
        return {
            'sales_by_category': analytics.get_sales_by_category(sales, products)
        }
    
    def get_full_analysis(self) -> dict:
        """
        Get complete analytics data combining all analyses.
        
        Returns:
            dict with all analytics data
        """
        logger.debug("Getting full analysis")
        
        return {
            **self.get_dashboard(),
            'products': self.get_product_analysis(),
            'profitability': self.get_profitability_analysis(),
            'daily': self.get_daily_analysis(),
            'categories': self.get_category_analysis()
        }