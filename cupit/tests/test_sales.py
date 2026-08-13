"""Tests for sales analytics."""

import pytest
from app.models import Product, Sale
from app.analytics import sales


class TestSalesAnalytics:
    """Test sales analytics calculations."""
    
    def test_revenue_calculation(self):
        """Test total revenue calculation."""
        products = [
            Product(id=1, name="Coffee", category="Drinks", purchase_price=50, selling_price=150),
            Product(id=2, name="Tea", category="Drinks", purchase_price=30, selling_price=100)
        ]
        sales_list = [
            Sale(id=1, product_id=1, quantity=2, date="2026-08-01", time="10:00"),
            Sale(id=2, product_id=2, quantity=3, date="2026-08-01", time="11:00")
        ]
        
        revenue = sales.calculate_total_revenue(sales_list, products)
        # 2 * 150 + 3 * 100 = 300 + 300 = 600
        assert revenue == 600.0
    
    def test_units_calculation(self):
        """Test total units calculation."""
        sales_list = [
            Sale(id=1, product_id=1, quantity=2, date="2026-08-01", time="10:00"),
            Sale(id=2, product_id=2, quantity=3, date="2026-08-01", time="11:00"),
            Sale(id=3, product_id=1, quantity=1, date="2026-08-01", time="12:00")
        ]
        
        units = sales.calculate_total_units(sales_list)
        assert units == 6
    
    def test_transaction_calculation(self):
        """Test transaction count calculation."""
        sales_list = [
            Sale(id=1, product_id=1, quantity=2, date="2026-08-01", time="10:00"),
            Sale(id=2, product_id=2, quantity=3, date="2026-08-01", time="11:00"),
            Sale(id=3, product_id=1, quantity=1, date="2026-08-01", time="12:00")
        ]
        
        count = sales.calculate_transaction_count(sales_list)
        assert count == 3
    
    def test_average_transaction_calculation(self):
        """Test average transaction value calculation."""
        products = [
            Product(id=1, name="Coffee", category="Drinks", purchase_price=50, selling_price=150)
        ]
        sales_list = [
            Sale(id=1, product_id=1, quantity=2, date="2026-08-01", time="10:00"),  # 300
            Sale(id=2, product_id=1, quantity=4, date="2026-08-01", time="11:00")   # 600
        ]
        
        avg = sales.calculate_average_transaction_value(sales_list, products)
        # (300 + 600) / 2 = 450
        assert avg == 450.0
    
    def test_empty_sales(self):
        """Test calculations with empty sales list."""
        products = [
            Product(id=1, name="Coffee", category="Drinks", purchase_price=50, selling_price=150)
        ]
        sales_list = []
        
        assert sales.calculate_total_revenue(sales_list, products) == 0.0
        assert sales.calculate_total_units(sales_list) == 0
        assert sales.calculate_transaction_count(sales_list) == 0
        assert sales.calculate_average_transaction_value(sales_list, products) == 0.0
