"""Source-independent domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Cafe:
    id: str
    name: str
    currency: str
    timezone: str


@dataclass(frozen=True, slots=True)
class Product:
    id: str
    name: str
    category: str
    current_price: Decimal
    current_cost: Decimal
    active: bool = True


@dataclass(frozen=True, slots=True)
class SaleLine:
    product_id: str
    quantity: int
    unit_price: Decimal
    unit_cost: Decimal
    discount: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("Sale line quantity must be positive")
        if self.unit_price < 0 or self.unit_cost < 0 or self.discount < 0:
            raise ValueError("Money values must not be negative")

    @property
    def revenue(self) -> Decimal:
        return self.unit_price * self.quantity - self.discount

    @property
    def gross_profit(self) -> Decimal:
        return (self.unit_price - self.unit_cost) * self.quantity - self.discount


@dataclass(frozen=True, slots=True)
class Receipt:
    id: str
    location_id: str
    closed_at: datetime
    lines: tuple[SaleLine, ...]

    def __post_init__(self) -> None:
        if self.closed_at.tzinfo is None:
            raise ValueError("Receipt datetime must include a timezone")
        if not self.lines:
            raise ValueError("Receipt must contain at least one sale line")
