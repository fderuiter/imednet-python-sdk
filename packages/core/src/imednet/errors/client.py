"""Client-side errors."""

from .base import ImednetError


class ClientError(ImednetError):
    """Raised for client-side errors (validation, configuration, misuse)."""

    pass
