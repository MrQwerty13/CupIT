"""Sales analytics module.

This module calculates sales-related metrics.
It operates ONLY on normalized Python models,
not on raw JSON or any specific data source.
"""

from collections import defaultdict
from typing import Dict, List

from app.models import Product, Sale


def calculate_total_revenue(sales: List[Sale], products: List[Product]) -> float:
    """Calculate total revenue from all sales.
    
    Args:
        sales: List of sale transactions.
        products: List of products for price lookup.
        
    Returns:
        Total revenue in currency units.
    """
    product_prices = {p.id: p.selling_price for p in products}
    total = 0.0
    
    for sale in sales:
        price = product_prices.get(sale.product_id, 0)
        total += price * sale.quantity
    
    return total


def calculate_total_units(sales: List[Sale]) -> int:
    """Calculate total number of units sold.
    
    Args:
        sales: List of sale transactions.
        
    Returns:
        Total units sold.
    """
    return sum(sale.quantity for sale in sales)


def calculate_transaction_count(sales: List[Sale]) -> int:
    """Calculate number of transactions.
    
    Args:
        sales: List of sale transactions.
        
    Returns:
        Number of transactions.
    """
    return len(sales)


def calculate_average_transaction_value(
    sales: List[Sale], 
    products: List[Product]
) -> float:
    """Calculate average transaction value.
    
    Args:
        sales: List of sale transactions.
        products: List of products for price lookup.
        
    Returns:
        Average transaction value.
    """
    total_revenue = calculate_total_revenue(sales, products)
    transaction_count = calculate_transaction_count(sales)
    
    if transaction_count == 0:
        return 0.0
    
    return total_revenue / transaction_count


def calculate_sales_by_day(
    sales: List[Sale], 
    products: List[Product]
) -> Dict[str, float]:
    """Calculate revenue by day.
    
    Args:
        sales: List of sale transactions.
        products: List of products for price lookup.
        
    Returns:
        Dictionary mapping date strings to revenue.
    """
    product_prices = {p.id: p.selling_price for p in products}
    daily_revenue: Dict[str, float] = defaultdict(float)
    
    for sale in sales:
        price = product_prices.get(sale.product_id, 0)
        revenue = price * sale.quantity
        daily_revenue[sale.date] += revenue
    
    return dict(daily_revenue)


def calculate_sales_by_category(
    sales: List[Sale], 
    products: List[Product]
) -> Dict[str, float]:
    """Calculate revenue by product category.
    
    Args:
        sales: List of sale transactions.
        products: List of products for price lookup.
        
    Returns:
        Dictionary mapping category names to revenue.
    """
    product_info = {p.id: p for p in products}
    category_revenue: Dict[str, float] = defaultdict(float)
    
    for sale in sales:
        product = product_info.get(sale.product_id)
        if product:
            revenue = product.selling_price * sale.quantity
            category_revenue[product.category] += revenue
    
    return dict(category_revenue)
