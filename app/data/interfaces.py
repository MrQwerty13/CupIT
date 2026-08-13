"""
CupIT - Coffee Shop Analytics Application
Data provider interfaces and implementations.

FUTURE:
Replace JsonDataProvider with CsvDataProvider,
ExcelDataProvider, DatabaseDataProvider or PosApiDataProvider.
"""

from abc import ABC, abstractmethod
import json
import logging
from pathlib import Path
from datetime import date

from app.models import Cafe, Product, Sale


logger = logging.getLogger(__name__)


class DataProvider(ABC):
    """
    Abstract base class for data providers.
    
    The analytics engine must NEVER directly read JSON files.
    Instead, it uses this abstraction to get normalized internal models.
    """
    
    @abstractmethod
    def get_cafe(self) -> Cafe:
        """Get cafe information."""
        pass
    
    @abstractmethod
    def get_products(self) -> list[Product]:
        """Get all products."""
        pass
    
    @abstractmethod
    def get_sales(self) -> list[Sale]:
        """Get all sales."""
        pass


class JsonDataProvider(DataProvider):
    """
    JSON file implementation of DataProvider.
    
    Responsible ONLY for:
    - reading JSON
    - validating basic structure
    - converting JSON into internal Python models
    
    It must NOT calculate analytics.
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        logger.info(f"Initializing JsonDataProvider with data directory: {self.data_dir}")
    
    def _load_json(self, filename: str) -> dict | list:
        """Load JSON file and return parsed data."""
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filepath}: {e}")
    
    def get_cafe(self) -> Cafe:
        """Load cafe data from JSON."""
        logger.debug("Loading cafe data")
        data = self._load_json("cafe.json")
        
        if isinstance(data, list):
            data = data[0] if data else {}
        
        return Cafe(
            id=data.get("id", 1),
            name=data.get("name", "Unknown Cafe"),
            currency=data.get("currency", "RUB")
        )
    
    def get_products(self) -> list[Product]:
        """Load products from JSON."""
        logger.debug("Loading products data")
        data = self._load_json("products.json")
        
        if not isinstance(data, list):
            raise ValueError("Products data must be a list")
        
        products = []
        for item in data:
            try:
                product = Product(
                    id=item["id"],
                    name=item["name"],
                    category=item["category"],
                    purchase_price=float(item["purchase_price"]),
                    selling_price=float(item["selling_price"])
                )
                products.append(product)
            except KeyError as e:
                raise ValueError(f"Missing required field in product: {e}")
        
        logger.info(f"Loaded {len(products)} products")
        return products
    
    def get_sales(self) -> list[Sale]:
        """Load sales from JSON."""
        logger.debug("Loading sales data")
        data = self._load_json("sales.json")
        
        if not isinstance(data, list):
            raise ValueError("Sales data must be a list")
        
        sales = []
        for item in data:
            try:
                sale_date = item["date"]
                if isinstance(sale_date, str):
                    sale_date = date.fromisoformat(sale_date)
                
                sale = Sale(
                    id=item["id"],
                    product_id=item["product_id"],
                    quantity=int(item["quantity"]),
                    date=sale_date,
                    time=item.get("time", "00:00")
                )
                sales.append(sale)
            except (KeyError, ValueError) as e:
                raise ValueError(f"Invalid sale data: {e}")
        
        logger.info(f"Loaded {len(sales)} sales")
        return sales