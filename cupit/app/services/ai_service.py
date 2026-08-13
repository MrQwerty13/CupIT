"""AI service for Ollama integration.

This service communicates with a locally running Ollama instance.
It receives structured analytics data and generates AI-powered insights.

Architecture:
    JSON → DataProvider → Analytics → Structured analytics result → AI Service → Ollama
"""

import json
import logging
from typing import Any, Dict, Optional

import requests

from app.core.config import Config
from app.core.exceptions import OllamaUnavailableException

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered insights using Ollama.
    
    The AI receives structured analytical information,
    not raw JSON files.
    """
    
    def __init__(self, config: Config):
        """Initialize AI service.
        
        Args:
            config: Application configuration.
        """
        self.ollama_host = config.OLLAMA_HOST
        self.model = config.OLLAMA_MODEL
        logger.info(f"AIService initialized with Ollama host: {self.ollama_host}")
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama service is available.
        
        Returns:
            True if Ollama is reachable, False otherwise.
        """
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException as e:
            logger.warning(f"Ollama unavailable: {e}")
            return False
    
    def analyze(self, analytics_data: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Send analytics data to Ollama and get AI response.
        
        Args:
            analytics_data: Structured analytics results.
            question: User's question about the data.
            
        Returns:
            Dictionary with AI answer.
            
        Raises:
            OllamaUnavailableException: If Ollama service is not reachable.
        """
        if not self._check_ollama_available():
            raise OllamaUnavailableException(
                "Ollama service is unavailable. Please ensure Ollama is running."
            )
        
        # Construct prompt with structured analytics data
        prompt = self._build_prompt(analytics_data, question)
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            answer = result.get("response", "No response generated")
            
            logger.info("Successfully received AI response")
            return {"answer": answer}
            
        except requests.Timeout:
            logger.error("Ollama request timed out")
            raise OllamaUnavailableException("Ollama request timed out")
        except requests.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            raise OllamaUnavailableException(f"Failed to communicate with Ollama: {e}")
    
    def _build_prompt(self, analytics_data: Dict[str, Any], question: str) -> str:
        """Build a structured prompt for the AI model.
        
        Args:
            analytics_data: Structured analytics results.
            question: User's question.
            
        Returns:
            Formatted prompt string.
        """
        # Format analytics data as readable text
        summary = analytics_data.get("summary", {})
        best_products = analytics_data.get("best_products", [])
        worst_products = analytics_data.get("worst_products", [])
        most_profitable = analytics_data.get("most_profitable", [])
        category_breakdown = analytics_data.get("category_breakdown", {})
        daily_sales = analytics_data.get("daily_sales", [])
        
        prompt = f"""You are an AI assistant for CupIT, a coffee shop analytics application.
Analyze the following business data and answer the user's question.

=== BUSINESS SUMMARY ===
Revenue: {summary.get('revenue', 0)} RUB
Profit: {summary.get('profit', 0)} RUB
Transactions: {summary.get('transactions', 0)}
Units Sold: {summary.get('units_sold', 0)}

=== TOP 5 BEST-SELLING PRODUCTS ===
"""
        for p in best_products:
            prompt += f"- {p.get('product', 'Unknown')}: {p.get('units_sold', 0)} units\n"
        
        prompt += "\n=== TOP 5 LOWEST-SELLING PRODUCTS ===\n"
        for p in worst_products:
            prompt += f"- {p.get('product', 'Unknown')}: {p.get('units_sold', 0)} units\n"
        
        prompt += "\n=== TOP 5 MOST PROFITABLE PRODUCTS ===\n"
        for p in most_profitable:
            prompt += f"- {p.get('product', 'Unknown')}: {p.get('total_profit', 0)} RUB total profit\n"
        
        prompt += "\n=== REVENUE BY CATEGORY ===\n"
        for category, revenue in category_breakdown.items():
            prompt += f"- {category}: {revenue} RUB\n"
        
        prompt += f"\n=== USER QUESTION ===\n{question}\n\nProvide a concise, actionable answer based on the data above."
        
        return prompt
