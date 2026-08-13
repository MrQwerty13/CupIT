"""
CupIT - Coffee Shop Analytics Application
Domain models for cafe, products, and sales.
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class Cafe:
    """Represents a coffee shop."""
    id: int
    name: str
    currency: str = "RUB"


@dataclass
class Product:
    """Represents a product sold in the cafe."""
    id: int
    name: str
    category: str
    purchase_price: float
    selling_price: float

    @property
    def profit_per_unit(self) -> float:
        """Calculate profit per unit."""
        return self.selling_price - self.purchase_price

    @property
    def profit_margin(self) -> float:
        """Calculate profit margin as percentage."""
        if self.selling_price == 0:
            return 0.0
        return (self.profit_per_unit / self.selling_price) * 100


@dataclass
class Sale:
    """Represents a single sale transaction."""
    id: int
    product_id: int
    quantity: int
    date: date
    time: str

    def __post_init__(self):
        """Convert date string to date object if needed."""
        if isinstance(self.date, str):
            self.date = date.fromisoformat(self.date)