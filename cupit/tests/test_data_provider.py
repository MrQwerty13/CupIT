"""Tests for data provider."""

import json
import pytest
from pathlib import Path
import tempfile
import os

from app.data.json_provider import JsonDataProvider
from app.core.exceptions import DataFileNotFoundError, DataValidationError


class TestJsonDataProvider:
    """Test JSON data provider."""
    
    def test_valid_json_loading(self, tmp_path):
        """Test loading valid JSON files."""
        # Create test data
        cafe_data = {"id": 1, "name": "Test Cafe", "currency": "RUB"}
        products_data = [
            {"id": 1, "name": "Coffee", "category": "Drinks", "purchase_price": 50, "selling_price": 150}
        ]
        sales_data = [
            {"id": 1, "product_id": 1, "quantity": 2, "date": "2026-08-01", "time": "10:00"}
        ]
        
        # Write test files
        (tmp_path / "cafe.json").write_text(json.dumps(cafe_data))
        (tmp_path / "products.json").write_text(json.dumps(products_data))
        (tmp_path / "sales.json").write_text(json.dumps(sales_data))
        
        # Test provider
        provider = JsonDataProvider(str(tmp_path))
        
        cafe = provider.get_cafe()
        assert cafe.id == 1
        assert cafe.name == "Test Cafe"
        
        products = provider.get_products()
        assert len(products) == 1
        assert products[0].name == "Coffee"
        
        sales = provider.get_sales()
        assert len(sales) == 1
        assert sales[0].quantity == 2
    
    def test_missing_file(self, tmp_path):
        """Test handling of missing files."""
        provider = JsonDataProvider(str(tmp_path))
        
        with pytest.raises(DataFileNotFoundError):
            provider.get_cafe()
    
    def test_malformed_json(self, tmp_path):
        """Test handling of malformed JSON."""
        (tmp_path / "cafe.json").write_text("{invalid json}")
        (tmp_path / "products.json").write_text("[]")
        (tmp_path / "sales.json").write_text("[]")
        
        provider = JsonDataProvider(str(tmp_path))
        
        with pytest.raises(DataValidationError):
            provider.get_cafe()
    
    def test_invalid_product_structure(self, tmp_path):
        """Test validation of product structure."""
        cafe_data = {"id": 1, "name": "Test"}
        products_data = [
            {"id": 1, "name": "Coffee"}  # Missing required fields
        ]
        sales_data = []
        
        (tmp_path / "cafe.json").write_text(json.dumps(cafe_data))
        (tmp_path / "products.json").write_text(json.dumps(products_data))
        (tmp_path / "sales.json").write_text(json.dumps(sales_data))
        
        provider = JsonDataProvider(str(tmp_path))
        
        with pytest.raises(DataValidationError):
            provider.get_products()
    
    def test_invalid_sale_structure(self, tmp_path):
        """Test validation of sale structure."""
        cafe_data = {"id": 1, "name": "Test"}
        products_data = [
            {"id": 1, "name": "Coffee", "category": "Drinks", "purchase_price": 50, "selling_price": 150}
        ]
        sales_data = [
            {"id": 1, "product_id": 1}  # Missing required fields
        ]
        
        (tmp_path / "cafe.json").write_text(json.dumps(cafe_data))
        (tmp_path / "products.json").write_text(json.dumps(products_data))
        (tmp_path / "sales.json").write_text(json.dumps(sales_data))
        
        provider = JsonDataProvider(str(tmp_path))
        
        with pytest.raises(DataValidationError):
            provider.get_sales()
