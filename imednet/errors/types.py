"""
Custom exception types for the iMednet SDK.
"""

from __future__ import annotations

from typing import Optional


class ImednetError(Exception):
    """Base class for all iMednet SDK exceptions."""

    def __init__(self, message: str, original_exception: Optional[Exception] = None) -> None:
        super().__init__(message)
        self.original_exception = original_exception


class NetworkError(ImednetError):
    """Raised when a network operation fails."""
    pass


class ValidationError(ImednetError, ValueError):
    """Raised when input validation fails."""
    pass


class ResourceNotFound(ImednetError, ValueError):
    """Raised when a requested resource is not found."""
    pass
