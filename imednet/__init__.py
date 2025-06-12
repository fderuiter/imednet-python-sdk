from importlib import metadata as _metadata

from .metrics import enable_metrics
from .sdk import ImednetSDK

__all__ = ["ImednetSDK", "enable_metrics", "__version__"]

try:
    __version__: str = _metadata.version("imednet-sdk")
except _metadata.PackageNotFoundError:  # local editable install
    __version__ = "0.0.0"
