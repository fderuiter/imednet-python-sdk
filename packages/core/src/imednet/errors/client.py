"""Client-side errors."""

from .base import ImednetError


class ClientError(ImednetError):
    """Raised for client-side errors (validation, configuration, misuse)."""

    def __init__(
        self,
        message: str = "",
        status_code: int | None = 400,
        code: int | None = None,
        status: str | None = "client_error",
    ) -> None:
        """Initialize the client error."""
        super().__init__(message, status_code=status_code, code=code, status=status)


class PaginationError(ClientError):
    """Raised when pagination metadata is malformed or inconsistent."""

    pass
