"""Replaceable data-provider contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from cupit.domain.models import Cafe, Product, Receipt


class DataProvider(ABC):
    """Return normalized objects regardless of the original source format."""

    @abstractmethod
    def get_cafe(self) -> Cafe:
        raise NotImplementedError

    @abstractmethod
    def get_products(self) -> tuple[Product, ...]:
        raise NotImplementedError

    @abstractmethod
    def get_receipts(self) -> tuple[Receipt, ...]:
        raise NotImplementedError


# Future CSV, 1C, iiko and PostgreSQL providers implement this interface.
# Analytics must never import or inspect the original source format.
