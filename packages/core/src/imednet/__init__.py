from importlib import metadata as _metadata

from .config import Config, load_config
from .core.base_client import BaseClient
from .core.retry import DefaultRetryPolicy, RetryPolicy, RetryState
from .sdk import AsyncImednetSDK, ImednetSDK
from .utils.typing import FilterScalar, FilterValue, ItemId, JsonDict

# Provide a backward-compatible alias
ImednetClient = ImednetSDK

__all__ = [
    "ImednetSDK",
    "AsyncImednetSDK",
    "ImednetClient",
    "BaseClient",
    "RetryPolicy",
    "RetryState",
    "DefaultRetryPolicy",
    "Config",
    "load_config",
    "JsonDict",
    "ItemId",
    "FilterValue",
    "FilterScalar",
    "__version__",
]

try:
    __version__: str = _metadata.version("imednet")
except _metadata.PackageNotFoundError:  # local editable install
    __version__ = "0.6.2"
