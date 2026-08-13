"""
CupIT - Coffee Shop Analytics Application
Configuration management.

Do not hardcode values throughout the code.
Use environment variables/configuration classes.
"""

import os
from pathlib import Path


class Config:
    """Application configuration."""
    
    # Base directory
    BASE_DIR = Path(__file__).parent.parent.parent
    
    # Data directory
    DATA_DIR = BASE_DIR / 'data'
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Ollama configuration
    OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://ollama:11434')
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama2')
    
    # Server settings
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    @classmethod
    def get_data_dir(cls) -> str:
        """Get data directory path."""
        return str(cls.DATA_DIR)