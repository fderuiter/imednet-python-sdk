"""Base errors."""


class ImednetError(Exception):
    """Base exception for all iMednet SDK errors."""

    def __init__(
        self,
        message: str = "",
        status_code: int | None = None,
        code: int | None = None,
        status: str | None = None,
    ) -> None:
        """Initialize the error."""
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.status = status
