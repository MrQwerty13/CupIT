"""Profitability analytics module.

This module calculates profitability metrics for products.
It operates ONLY on normalized Python models,
not on raw JSON or any specific data source.
"""

from collections import defaultdict
from typing import Dict, List

from app.models import Product, Sale


def calculate_profit_by_product(
    sales: List[Sale], 
    products: List[Product]
) -> Dict[int, Dict[str, float]]:
    """Calculate profit metrics per product.
    
    Args:
        sales: List of sale transactions.
        products: List of products.
        
    Returns:
        Dictionary mapping product IDs to profit metrics.
    """
    product_map = {p.id: p for p in products}
    units_by_product: Dict[int, int] = defaultdict(int)
    
    for sale in sales:
        units_by_product[sale.product_id] += sale.quantity
    
    result = {}
    for product in products:
        units_sold = units_by_product.get(product.id, 0)
        
        result[product.id] = {
            "profit_per_unit": round(product.profit_per_unit, 2),
            "profit_margin": round(product.profit_margin, 2),
            "total_profit": round(product.profit_per_unit * units_sold, 2),
            "units_sold": units_sold
        }
    
    return result


def get_most_profitable_products(
    sales: List[Sale], 
    products: List[Product],
    limit: int = 10,
    by: str = "total_profit"
) -> List[Dict]:
    """Get most profitable products.
    
    Args:
        sales: List of sale transactions.
        products: List of products.
        limit: Maximum number of products to return.
        by: Sort by 'profit_per_unit', 'profit_margin', or 'total_profit'.
        
    Returns:
        List of dictionaries with product name and profit metrics.
    """
    profit_data = calculate_profit_by_product(sales, products)
    product_map = {p.id: p for p in products}
    
    # Sort by specified metric (descending)
    sorted_products = sorted(
        profit_data.items(),
        key=lambda x: x[1].get(by, 0),
        reverse=True
    )
    
    result = []
    for product_id, metrics in sorted_products[:limit]:
        product = product_map.get(product_id)
        if product:
            result.append({
                "product": product.name,
                "category": product.category,
                "profit_per_unit": metrics["profit_per_unit"],
                "profit_margin": metrics["profit_margin"],
                "total_profit": metrics["total_profit"],
                "units_sold": metrics["units_sold"]
            })
    
    return result


def get_least_profitable_products(
    sales: List[Sale], 
    products: List[Product],
    limit: int = 10,
    by: str = "total_profit"
) -> List[Dict]:
    """Get least profitable products.
    
    Args:
        sales: List of sale transactions.
        products: List of products.
        limit: Maximum number of products to return.
        by: Sort by 'profit_per_unit', 'profit_margin', or 'total_profit'.
        
    Returns:
        List of dictionaries with product name and profit metrics.
    """
    profit_data = calculate_profit_by_product(sales, products)
    product_map = {p.id: p for p in products}
    
    # Sort by specified metric (ascending)
    sorted_products = sorted(
        profit_data.items(),
        key=lambda x: x[1].get(by, 0)
    )
    
    result = []
    for product_id, metrics in sorted_products[:limit]:
        product = product_map.get(product_id)
        if product:
            result.append({
                "product": product.name,
                "category": product.category,
                "profit_per_unit": metrics["profit_per_unit"],
                "profit_margin": metrics["profit_margin"],
                "total_profit": metrics["total_profit"],
                "units_sold": metrics["units_sold"]
            })
    
    return result
