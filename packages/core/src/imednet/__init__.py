from importlib import metadata as _metadata

from .config import Config, load_config
from .core.base_client import BaseClient
from .core.retry import DefaultRetryPolicy, RetryPolicy, RetryState
from .errors import PluginLoadError
from .errors.orchestration import FilterConflictError, OrchestratorError
from .orchestration import (
    MultiStudyOrchestrator,
    OrchestratorResult,
    StudyWorkerCallable,
)
from .plugins import PluginProtocol, WorkflowsNamespaceProtocol
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
    "MultiStudyOrchestrator",
    "OrchestratorResult",
    "StudyWorkerCallable",
    "OrchestratorError",
    "FilterConflictError",
    "PluginLoadError",
    "PluginProtocol",
    "WorkflowsNamespaceProtocol",
    "__version__",
]

try:
    __version__: str = _metadata.version("imednet")
except _metadata.PackageNotFoundError:  # local editable install
    __version__ = "0.7.0"
