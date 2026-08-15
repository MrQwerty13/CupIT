"""Application-specific exceptions mapped to stable API errors."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CupitError(Exception):
    message: str
    code: str = "CUPIT_ERROR"
    status_code: int = 500
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details:
            result["details"] = self.details
        return result


class DataSourceError(CupitError):
    def __init__(self, message: str, code: str = "DATA_SOURCE_ERROR") -> None:
        super().__init__(message=message, code=code, status_code=500)


class DataValidationError(CupitError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            code="DATA_VALIDATION_FAILED",
            status_code=422,
            details=details or {},
        )


class InvalidRequestError(CupitError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="INVALID_REQUEST", status_code=400)


class AiUnavailableError(CupitError):
    def __init__(self, message: str = "Local AI service is unavailable") -> None:
        super().__init__(message=message, code="AI_UNAVAILABLE", status_code=503)
