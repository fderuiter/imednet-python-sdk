"""Export-sink error types."""

from .base import ImednetError


class ExportError(ImednetError):
    """Raised when an export sink cannot write a batch or finalize a destination."""

    pass


class ExportConfigurationError(ExportError):
    """Raised when a sink is misconfigured (missing credentials, invalid parameters)."""

    pass


class ExportBatchError(ExportError):
    """Raised when a single batch write fails after all retries are exhausted."""

    def __init__(self, message: str, *, batch_id: str) -> None:
        super().__init__(message)
        self.batch_id = batch_id
