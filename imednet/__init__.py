from importlib import metadata as _metadata

from .sdk import ImednetSDK
from .vault_client import VaultClient

__all__ = ["ImednetSDK", "VaultClient", "__version__"]

try:
    __version__: str = _metadata.version("imednet-sdk")
except _metadata.PackageNotFoundError:  # local editable install
    __version__ = "0.0.0"
