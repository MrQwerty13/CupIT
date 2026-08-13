"""Data provider interfaces.

FUTURE:
This interface defines the contract for all data providers.
Future implementations can include:
- CsvDataProvider
- ExcelDataProvider
- DatabaseDataProvider (PostgreSQL, MySQL)
- PosApiDataProvider (1C, iiko, Poster, etc.)
- CloudApiDataProvider

The analytics engine depends ONLY on this interface,
not on any specific implementation.
"""

from abc import ABC, abstractmethod
from typing import List

from app.models import Cafe, Product, Sale


class DataProvider(ABC):
    """Abstract base class for all data providers.
    
    Analytics must remain independent of the original data source.
    This abstraction allows swapping data sources without changing
    the analytics engine.
    """
    
    @abstractmethod
    def get_cafe(self) -> Cafe:
        """Get cafe information.
        
        Returns:
            Cafe object with cafe details.
        """
        pass
    
    @abstractmethod
    def get_products(self) -> List[Product]:
        """Get all products.
        
        Returns:
            List of Product objects.
        """
        pass
    
    @abstractmethod
    def get_sales(self) -> List[Sale]:
        """Get all sales.
        
        Returns:
            List of Sale objects.
        """
        pass
