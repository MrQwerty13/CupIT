"""Tests for profitability analytics."""

import pytest
from app.models import Product, Sale
from app.analytics import profitability


class TestProfitabilityAnalytics:
    """Test profitability analytics calculations."""
    
    def test_profit_calculation(self):
        """Test profit per unit calculation."""
        prod = Product(id=1, name="Coffee", category="Drinks", purchase_price=50, selling_price=150)
        products_list = [prod]
        sales_list = [
            Sale(id=1, product_id=1, quantity=3, date="2026-08-01", time="10:00")
        ]
        
        profit_data = profitability.calculate_profit_by_product(sales_list, products_list)
        
        assert profit_data[1]["profit_per_unit"] == 100.0  # 150 - 50
        assert profit_data[1]["total_profit"] == 300.0     # 100 * 3
    
    def test_profit_margin_calculation(self):
        """Test profit margin calculation."""
        prod = Product(id=1, name="Coffee", category="Drinks", purchase_price=50, selling_price=150)
        products_list = [prod]
        sales_list = []
        
        profit_data = profitability.calculate_profit_by_product(sales_list, products_list)
        
        # Profit margin = (150 - 50) / 150 * 100 = 66.67%
        assert profit_data[1]["profit_margin"] == pytest.approx(66.67, rel=0.01)
    
    def test_total_profit_calculation(self):
        """Test total profit calculation."""
        prod1 = Product(id=1, name="Coffee", category="Drinks", purchase_price=50, selling_price=150)
        prod2 = Product(id=2, name="Tea", category="Drinks", purchase_price=30, selling_price=100)
        products_list = [prod1, prod2]
        
        sales_list = [
            Sale(id=1, product_id=1, quantity=5, date="2026-08-01", time="10:00"),  # profit: 500
            Sale(id=2, product_id=2, quantity=10, date="2026-08-01", time="11:00")  # profit: 700
        ]
        
        profit_data = profitability.calculate_profit_by_product(sales_list, products_list)
        
        assert profit_data[1]["total_profit"] == 500.0  # (150-50) * 5
        assert profit_data[2]["total_profit"] == 700.0  # (100-30) * 10
    
    def test_most_profitable_products(self):
        """Test most profitable products ranking."""
        prod1 = Product(id=1, name="Coffee", category="Drinks", purchase_price=50, selling_price=150)
        prod2 = Product(id=2, name="Tea", category="Drinks", purchase_price=30, selling_price=100)
        products_list = [prod1, prod2]
        
        sales_list = [
            Sale(id=1, product_id=1, quantity=5, date="2026-08-01", time="10:00"),  # profit: 500
            Sale(id=2, product_id=2, quantity=10, date="2026-08-01", time="11:00")  # profit: 700
        ]
        
        most_profitable = profitability.get_most_profitable_products(sales_list, products_list)
        
        assert most_profitable[0]["product"] == "Tea"
        assert most_profitable[0]["total_profit"] == 700.0
