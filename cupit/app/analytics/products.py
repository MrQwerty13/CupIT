"""Product analytics module.

This module calculates product-related metrics.
It operates ONLY on normalized Python models,
not on raw JSON or any specific data source.
"""

from collections import defaultdict
from typing import Dict, List, Tuple

from app.models import Product, Sale


def calculate_units_sold_by_product(
    sales: List[Sale], 
    products: List[Product]
) -> Dict[int, int]:
    """Calculate units sold per product.
    
    Args:
        sales: List of sale transactions.
        products: List of products.
        
    Returns:
        Dictionary mapping product IDs to units sold.
    """
    units_by_product: Dict[int, int] = defaultdict(int)
    
    for sale in sales:
        units_by_product[sale.product_id] += sale.quantity
    
    return dict(units_by_product)


def get_best_selling_products(
    sales: List[Sale], 
    products: List[Product],
    limit: int = 10
) -> List[Dict]:
    """Get best-selling products ranked by units sold.
    
    Args:
        sales: List of sale transactions.
        products: List of products.
        limit: Maximum number of products to return.
        
    Returns:
        List of dictionaries with product name and units sold.
    """
    product_map = {p.id: p for p in products}
    units_by_product = calculate_units_sold_by_product(sales, products)
    
    # Sort by units sold (descending)
    sorted_products = sorted(
        units_by_product.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    result = []
    for product_id, units in sorted_products[:limit]:
        product = product_map.get(product_id)
        if product:
            result.append({
                "product": product.name,
                "units_sold": units
            })
    
    return result


def get_highest_revenue_products(
    sales: List[Sale], 
    products: List[Product],
    limit: int = 10
) -> List[Dict]:
    """Get highest-revenue products.
    
    Args:
        sales: List of sale transactions.
        products: List of products.
        limit: Maximum number of products to return.
        
    Returns:
        List of dictionaries with product name and revenue.
    """
    product_map = {p.id: p for p in products}
    revenue_by_product: Dict[int, float] = defaultdict(float)
    
    for sale in sales:
        product = product_map.get(sale.product_id)
        if product:
            revenue = product.selling_price * sale.quantity
            revenue_by_product[sale.product_id] += revenue
    
    # Sort by revenue (descending)
    sorted_products = sorted(
        revenue_by_product.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    result = []
    for product_id, revenue in sorted_products[:limit]:
        product = product_map.get(product_id)
        if product:
            result.append({
                "product": product.name,
                "revenue": round(revenue, 2)
            })
    
    return result


def get_least_selling_products(
    sales: List[Sale], 
    products: List[Product],
    limit: int = 10
) -> List[Dict]:
    """Get least-selling products.
    
    Args:
        sales: List of sale transactions.
        products: List of products.
        limit: Maximum number of products to return.
        
    Returns:
        List of dictionaries with product name and units sold.
    """
    product_map = {p.id: p for p in products}
    units_by_product = calculate_units_sold_by_product(sales, products)
    
    # Include products with zero sales
    all_products_with_sales = {p.id: units_by_product.get(p.id, 0) for p in products}
    
    # Sort by units sold (ascending)
    sorted_products = sorted(
        all_products_with_sales.items(),
        key=lambda x: x[1]
    )
    
    result = []
    for product_id, units in sorted_products[:limit]:
        product = product_map.get(product_id)
        if product:
            result.append({
                "product": product.name,
                "units_sold": units
            })
    
    return result
