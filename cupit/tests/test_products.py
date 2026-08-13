"""Tests for product analytics."""

import pytest
from app.models import Product, Sale
from app.analytics import products


class TestProductAnalytics:
    """Test product analytics calculations."""
    
    def test_best_selling_product(self):
        """Test best-selling product identification."""
        prod1 = Product(id=1, name="Coffee", category="Drinks", purchase_price=50, selling_price=150)
        prod2 = Product(id=2, name="Tea", category="Drinks", purchase_price=30, selling_price=100)
        products_list = [prod1, prod2]
        
        sales_list = [
            Sale(id=1, product_id=1, quantity=10, date="2026-08-01", time="10:00"),
            Sale(id=2, product_id=2, quantity=5, date="2026-08-01", time="11:00")
        ]
        
        best = products.get_best_selling_products(sales_list, products_list)
        assert len(best) == 2
        assert best[0]["product"] == "Coffee"
        assert best[0]["units_sold"] == 10
    
    def test_least_selling_product(self):
        """Test least-selling product identification."""
        prod1 = Product(id=1, name="Coffee", category="Drinks", purchase_price=50, selling_price=150)
        prod2 = Product(id=2, name="Tea", category="Drinks", purchase_price=30, selling_price=100)
        prod3 = Product(id=3, name="Juice", category="Drinks", purchase_price=40, selling_price=120)
        products_list = [prod1, prod2, prod3]
        
        sales_list = [
            Sale(id=1, product_id=1, quantity=10, date="2026-08-01", time="10:00"),
            Sale(id=2, product_id=2, quantity=5, date="2026-08-01", time="11:00")
            # prod3 has no sales
        ]
        
        least = products.get_least_selling_products(sales_list, products_list)
        assert least[0]["product"] == "Juice"
        assert least[0]["units_sold"] == 0
    
    def test_highest_revenue_product(self):
        """Test highest-revenue product identification."""
        prod1 = Product(id=1, name="Coffee", category="Drinks", purchase_price=50, selling_price=150)
        prod2 = Product(id=2, name="Tea", category="Drinks", purchase_price=30, selling_price=100)
        products_list = [prod1, prod2]
        
        sales_list = [
            Sale(id=1, product_id=1, quantity=2, date="2026-08-01", time="10:00"),  # 300
            Sale(id=2, product_id=2, quantity=4, date="2026-08-01", time="11:00")   # 400
        ]
        
        highest = products.get_highest_revenue_products(sales_list, products_list)
        assert highest[0]["product"] == "Tea"
        assert highest[0]["revenue"] == 400.0
