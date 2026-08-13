"""Domain models for CupIT."""

from dataclasses import dataclass


@dataclass
class Cafe:
    """Represents a cafe location."""
    id: int
    name: str
    currency: str = "RUB"


@dataclass
class Product:
    """Represents a product in the cafe."""
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
        """Calculate profit margin percentage."""
        if self.selling_price == 0:
            return 0.0
        return (self.profit_per_unit / self.selling_price) * 100


@dataclass
class Sale:
    """Represents a sale transaction."""
    id: int
    product_id: int
    quantity: int
    date: str  # Format: YYYY-MM-DD
    time: str  # Format: HH:MM
