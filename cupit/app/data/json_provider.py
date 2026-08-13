"""JSON data provider implementation.

This provider reads data from JSON files and converts them
into normalized Python models.

FUTURE:
Replace or extend this with:
- CsvDataProvider: reads from CSV files
- ExcelDataProvider: reads from .xlsx files using openpyxl
- DatabaseDataProvider: reads from PostgreSQL/MySQL
- PosApiDataProvider: fetches from POS system APIs (1C, iiko, etc.)
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from app.core.exceptions import DataFileNotFoundError, DataValidationError
from app.data.interfaces import DataProvider
from app.models import Cafe, Product, Sale

logger = logging.getLogger(__name__)


class JsonDataProvider(DataProvider):
    """JSON file data provider.
    
    Responsible ONLY for:
    - Reading JSON files
    - Validating basic structure
    - Converting JSON into internal Python models
    
    Must NOT calculate analytics.
    """
    
    def __init__(self, data_dir: str):
        """Initialize JSON data provider.
        
        Args:
            data_dir: Directory containing JSON data files.
        """
        self.data_dir = Path(data_dir)
        logger.info(f"JsonDataProvider initialized with data directory: {data_dir}")
    
    def _load_json_file(self, filename: str) -> Any:
        """Load and parse a JSON file.
        
        Args:
            filename: Name of the JSON file to load.
            
        Returns:
            Parsed JSON data.
            
        Raises:
            DataFileNotFoundError: If the file does not exist.
            DataValidationError: If the JSON is malformed.
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise DataFileNotFoundError(f"Data file not found: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"Loaded JSON file: {filename}")
            return data
        except json.JSONDecodeError as e:
            raise DataValidationError(f"Invalid JSON in {filename}: {e}")
    
    def _validate_cafe(self, data: Dict[str, Any]) -> None:
        """Validate cafe data structure."""
        required_fields = ['id', 'name']
        for field in required_fields:
            if field not in data:
                raise DataValidationError(f"Cafe data missing required field: {field}")
    
    def _validate_product(self, data: Dict[str, Any]) -> None:
        """Validate product data structure."""
        required_fields = ['id', 'name', 'category', 'purchase_price', 'selling_price']
        for field in required_fields:
            if field not in data:
                raise DataValidationError(f"Product data missing required field: {field}")
    
    def _validate_sale(self, data: Dict[str, Any]) -> None:
        """Validate sale data structure."""
        required_fields = ['id', 'product_id', 'quantity', 'date', 'time']
        for field in required_fields:
            if field not in data:
                raise DataValidationError(f"Sale data missing required field: {field}")
    
    def get_cafe(self) -> Cafe:
        """Get cafe information from JSON file.
        
        Returns:
            Cafe object with cafe details.
            
        Raises:
            DataFileNotFoundError: If cafe.json does not exist.
            DataValidationError: If cafe data is invalid.
        """
        data = self._load_json_file('cafe.json')
        
        # Handle both single object and list with one object
        if isinstance(data, list):
            if len(data) == 0:
                raise DataValidationError("Cafe data is empty")
            data = data[0]
        
        self._validate_cafe(data)
        
        cafe = Cafe(
            id=data['id'],
            name=data['name'],
            currency=data.get('currency', 'RUB')
        )
        logger.info(f"Loaded cafe: {cafe.name}")
        return cafe
    
    def get_products(self) -> List[Product]:
        """Get all products from JSON file.
        
        Returns:
            List of Product objects.
            
        Raises:
            DataFileNotFoundError: If products.json does not exist.
            DataValidationError: If product data is invalid.
        """
        data = self._load_json_file('products.json')
        
        if not isinstance(data, list):
            raise DataValidationError("Products data must be a list")
        
        products = []
        for item in data:
            self._validate_product(item)
            product = Product(
                id=item['id'],
                name=item['name'],
                category=item['category'],
                purchase_price=float(item['purchase_price']),
                selling_price=float(item['selling_price'])
            )
            products.append(product)
        
        logger.info(f"Loaded {len(products)} products")
        return products
    
    def get_sales(self) -> List[Sale]:
        """Get all sales from JSON file.
        
        Returns:
            List of Sale objects.
            
        Raises:
            DataFileNotFoundError: If sales.json does not exist.
            DataValidationError: If sale data is invalid.
        """
        data = self._load_json_file('sales.json')
        
        if not isinstance(data, list):
            raise DataValidationError("Sales data must be a list")
        
        sales = []
        for item in data:
            self._validate_sale(item)
            sale = Sale(
                id=item['id'],
                product_id=int(item['product_id']),
                quantity=int(item['quantity']),
                date=item['date'],
                time=item['time']
            )
            sales.append(sale)
        
        logger.info(f"Loaded {len(sales)} sales")
        return sales
