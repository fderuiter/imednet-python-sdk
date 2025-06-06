"""iMednet SDK public package initializer."""

from importlib import metadata as _metadata

from .async_sdk import AsyncImednetSDK
from .sdk import ImednetSDK

__all__ = ["ImednetSDK", "AsyncImednetSDK", "__version__"]

try:
    __version__: str = _metadata.version("imednet-sdk")
except _metadata.PackageNotFoundError:  # local editable install
    __version__ = "0.0.0"
