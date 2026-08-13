"""Daily analytics module.

This module calculates daily metrics.
It operates ONLY on normalized Python models,
not on raw JSON or any specific data source.
"""

from collections import defaultdict
from typing import Dict, List

from app.models import Product, Sale


def calculate_daily_analytics(
    sales: List[Sale], 
    products: List[Product]
) -> List[Dict]:
    """Calculate analytics per day.
    
    Args:
        sales: List of sale transactions.
        products: List of products.
        
    Returns:
        List of dictionaries with daily metrics.
    """
    product_map = {p.id: p for p in products}
    
    # Aggregate data by date
    daily_data: Dict[str, Dict] = defaultdict(lambda: {
        "revenue": 0.0,
        "profit": 0.0,
        "transactions": 0,
        "units_sold": 0
    })
    
    for sale in sales:
        product = product_map.get(sale.product_id)
        if not product:
            continue
        
        date = sale.date
        revenue = product.selling_price * sale.quantity
        profit = product.profit_per_unit * sale.quantity
        
        daily_data[date]["revenue"] += revenue
        daily_data[date]["profit"] += profit
        daily_data[date]["transactions"] += 1
        daily_data[date]["units_sold"] += sale.quantity
    
    # Convert to list and sort by date
    result = []
    for date in sorted(daily_data.keys()):
        data = daily_data[date]
        result.append({
            "date": date,
            "revenue": round(data["revenue"], 2),
            "profit": round(data["profit"], 2),
            "transactions": data["transactions"],
            "units_sold": data["units_sold"]
        })
    
    return result
