"""API schemas for request/response validation."""

from typing import Any, Dict, List


class HealthResponse:
    """Health check response schema."""
    
    @staticmethod
    def example() -> Dict[str, str]:
        return {
            "status": "healthy",
            "service": "CupIT API"
        }


class DashboardResponse:
    """Dashboard response schema."""
    
    @staticmethod
    def example() -> Dict[str, Any]:
        return {
            "revenue": 150000.0,
            "profit": 82000.0,
            "transactions": 500,
            "units_sold": 720,
            "average_transaction": 300.0
        }


class ProductResponse:
    """Product response schema."""
    
    @staticmethod
    def example() -> Dict[str, Any]:
        return {
            "id": 1,
            "name": "Cappuccino",
            "category": "Coffee",
            "purchase_price": 70.0,
            "selling_price": 250.0,
            "profit_per_unit": 180.0,
            "profit_margin": 72.0
        }


class BestSellingResponse:
    """Best-selling products response schema."""
    
    @staticmethod
    def example() -> List[Dict[str, Any]]:
        return [
            {
                "product": "Cappuccino",
                "units_sold": 153
            }
        ]


class ProfitableProductResponse:
    """Most profitable products response schema."""
    
    @staticmethod
    def example() -> List[Dict[str, Any]]:
        return [
            {
                "product": "Cappuccino",
                "category": "Coffee",
                "profit_per_unit": 180.0,
                "profit_margin": 72.0,
                "total_profit": 27540.0,
                "units_sold": 153
            }
        ]


class DailySalesResponse:
    """Daily sales response schema."""
    
    @staticmethod
    def example() -> List[Dict[str, Any]]:
        return [
            {
                "date": "2026-08-01",
                "revenue": 12500.0,
                "profit": 6700.0,
                "transactions": 48,
                "units_sold": 65
            }
        ]


class AIAnalyzeRequest:
    """AI analyze request schema."""
    
    @staticmethod
    def example() -> Dict[str, str]:
        return {
            "question": "What should the cafe owner improve?"
        }


class AIAnalyzeResponse:
    """AI analyze response schema."""
    
    @staticmethod
    def example() -> Dict[str, str]:
        return {
            "answer": "Based on the analytics data..."
        }


class ErrorResponse:
    """Error response schema."""
    
    @staticmethod
    def example(message: str = "Error message") -> Dict[str, str]:
        return {
            "error": message
        }
