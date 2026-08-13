"""
CupIT - Coffee Shop Analytics Application
Analytics modules for sales, products, profitability, and dates.

Analytics must remain independent of the original data source.
They operate only on normalized Python objects.
"""

from datetime import date
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Product, Sale


def calculate_total_revenue(sales: list['Sale'], products: dict[int, 'Product']) -> float:
    """Calculate total revenue from all sales."""
    total = 0.0
    for sale in sales:
        product = products.get(sale.product_id)
        if product:
            total += product.selling_price * sale.quantity
    return total


def calculate_total_units(sales: list['Sale']) -> int:
    """Calculate total number of units sold."""
    return sum(sale.quantity for sale in sales)


def calculate_transaction_count(sales: list['Sale']) -> int:
    """Calculate number of transactions (unique sales records)."""
    return len(sales)


def calculate_average_transaction_value(sales: list['Sale'], products: dict[int, 'Product']) -> float:
    """Calculate average transaction value."""
    total_revenue = calculate_total_revenue(sales, products)
    transaction_count = calculate_transaction_count(sales)
    
    if transaction_count == 0:
        return 0.0
    
    return total_revenue / transaction_count


def calculate_total_profit(sales: list['Sale'], products: dict[int, 'Product']) -> float:
    """Calculate total profit from all sales."""
    total = 0.0
    for sale in sales:
        product = products.get(sale.product_id)
        if product:
            total += product.profit_per_unit * sale.quantity
    return total


def get_sales_by_day(sales: list['Sale'], products: dict[int, 'Product']) -> list[dict]:
    """Calculate sales metrics grouped by day."""
    daily_data = defaultdict(lambda: {
        'revenue': 0.0,
        'profit': 0.0,
        'transactions': 0,
        'units_sold': 0
    })
    
    for sale in sales:
        product = products.get(sale.product_id)
        if not product:
            continue
        
        day_key = sale.date
        daily_data[day_key]['revenue'] += product.selling_price * sale.quantity
        daily_data[day_key]['profit'] += product.profit_per_unit * sale.quantity
        daily_data[day_key]['transactions'] += 1
        daily_data[day_key]['units_sold'] += sale.quantity
    
    # Convert to sorted list
    result = []
    for day in sorted(daily_data.keys()):
        data = daily_data[day]
        result.append({
            'date': day.isoformat() if isinstance(day, date) else str(day),
            'revenue': data['revenue'],
            'profit': data['profit'],
            'transactions': data['transactions'],
            'units_sold': data['units_sold']
        })
    
    return result


def get_sales_by_category(sales: list['Sale'], products: dict[int, 'Product']) -> dict[str, float]:
    """Calculate revenue by product category."""
    category_revenue = defaultdict(float)
    
    for sale in sales:
        product = products.get(sale.product_id)
        if product:
            category_revenue[product.category] += product.selling_price * sale.quantity
    
    return dict(category_revenue)


def get_best_selling_products(sales: list['Sale'], products: dict[int, 'Product'], limit: int = 10) -> list[dict]:
    """Get products ranked by units sold."""
    product_units = defaultdict(int)
    product_revenue = defaultdict(float)
    
    for sale in sales:
        product = products.get(sale.product_id)
        if product:
            product_units[sale.product_id] += sale.quantity
            product_revenue[sale.product_id] += product.selling_price * sale.quantity
    
    # Sort by units sold
    sorted_products = sorted(
        product_units.items(),
        key=lambda x: x[1],
        reverse=True
    )[:limit]
    
    result = []
    for product_id, units_sold in sorted_products:
        product = products[product_id]
        result.append({
            'id': product.id,
            'name': product.name,
            'category': product.category,
            'units_sold': units_sold,
            'revenue': product_revenue[product_id]
        })
    
    return result


def get_highest_revenue_products(sales: list['Sale'], products: dict[int, 'Product'], limit: int = 10) -> list[dict]:
    """Get products ranked by total revenue."""
    product_revenue = defaultdict(float)
    product_units = defaultdict(int)
    
    for sale in sales:
        product = products.get(sale.product_id)
        if product:
            product_revenue[sale.product_id] += product.selling_price * sale.quantity
            product_units[sale.product_id] += sale.quantity
    
    # Sort by revenue
    sorted_products = sorted(
        product_revenue.items(),
        key=lambda x: x[1],
        reverse=True
    )[:limit]
    
    result = []
    for product_id, revenue in sorted_products:
        product = products[product_id]
        result.append({
            'id': product.id,
            'name': product.name,
            'category': product.category,
            'revenue': revenue,
            'units_sold': product_units[product_id]
        })
    
    return result


def get_lowest_selling_products(sales: list['Sale'], products: dict[int, 'Product'], limit: int = 10) -> list[dict]:
    """Get products with smallest number of sales."""
    product_units = defaultdict(int)
    
    for sale in sales:
        product = products.get(sale.product_id)
        if product:
            product_units[sale.product_id] += sale.quantity
    
    # Sort by units sold (ascending)
    sorted_products = sorted(
        product_units.items(),
        key=lambda x: x[1]
    )[:limit]
    
    result = []
    for product_id, units_sold in sorted_products:
        product = products[product_id]
        result.append({
            'id': product.id,
            'name': product.name,
            'category': product.category,
            'units_sold': units_sold
        })
    
    return result


def get_most_profitable_products(sales: list['Sale'], products: dict[int, 'Product'], limit: int = 10) -> list[dict]:
    """Get products ranked by total profit."""
    product_profit = defaultdict(float)
    product_units = defaultdict(int)
    
    for sale in sales:
        product = products.get(sale.product_id)
        if product:
            product_profit[sale.product_id] += product.profit_per_unit * sale.quantity
            product_units[sale.product_id] += sale.quantity
    
    # Sort by total profit
    sorted_products = sorted(
        product_profit.items(),
        key=lambda x: x[1],
        reverse=True
    )[:limit]
    
    result = []
    for product_id, total_profit in sorted_products:
        product = products[product_id]
        result.append({
            'id': product.id,
            'name': product.name,
            'category': product.category,
            'profit_per_unit': product.profit_per_unit,
            'profit_margin': product.profit_margin,
            'total_profit': total_profit,
            'units_sold': product_units[product_id]
        })
    
    return result