"""Custom exceptions for CupIT application."""


class CupITException(Exception):
    """Base exception for CupIT."""
    pass


class DataProviderException(CupITException):
    """Exception raised by data providers."""
    pass


class DataValidationError(DataProviderException):
    """Exception raised when data validation fails."""
    pass


class DataFileNotFoundError(DataProviderException):
    """Exception raised when a data file is not found."""
    pass


class AnalyticsException(CupITException):
    """Exception raised during analytics calculations."""
    pass


class AIServiceException(CupITException):
    """Exception raised by AI service."""
    pass


class OllamaUnavailableException(AIServiceException):
    """Exception raised when Ollama service is unavailable."""
    pass
