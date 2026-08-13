"""
CupIT - Coffee Shop Analytics Application
Custom exceptions and error handlers.
"""

from functools import wraps
from flask import jsonify
import logging


logger = logging.getLogger(__name__)


class CupitError(Exception):
    """Base exception for CupIT application."""
    status_code = 500
    
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.message = message
        if status_code:
            self.status_code = status_code


class DataNotFoundError(CupitError):
    """Raised when requested data is not found."""
    status_code = 404


class DataValidationError(CupitError):
    """Raised when data validation fails."""
    status_code = 400


def handle_api_error(f):
    """Decorator to handle API errors gracefully."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except CupitError as e:
            logger.warning(f"API error: {e.message}")
            return jsonify({'error': e.message}), e.status_code
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return jsonify({'error': 'Data file not found'}), 404
        except ValueError as e:
            logger.error(f"Value error: {e}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    return wrapper