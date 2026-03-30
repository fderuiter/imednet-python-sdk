"""Network errors."""

from .base import ImednetError


class RequestError(ImednetError):
    """Raised when a network request fails after retries."""
    pass
