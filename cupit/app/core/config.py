"""Application configuration."""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration loaded from environment variables."""
    
    # Flask settings
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Ollama settings
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2")
    
    # Data settings
    DATA_DIR: str = os.getenv("DATA_DIR", "/app/data")
    
    # API settings
    API_PORT: int = int(os.getenv("API_PORT", "5000"))
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
