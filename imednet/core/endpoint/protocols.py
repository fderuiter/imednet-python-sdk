from typing import Any, Dict, Optional, Protocol, Type, runtime_checkable

from imednet.core.protocols import AsyncRequestorProtocol
from imednet.models.json_base import JsonModel


@runtime_checkable
class EndpointProtocol(Protocol):
    """Protocol defining the interface for endpoint classes."""

    PATH: str
    MODEL: Type[JsonModel]
    _id_param: str
    _cache_name: Optional[str]
    requires_study_key: bool
    PAGE_SIZE: int
    _pop_study_filter: bool
    _missing_study_exception: type[Exception]

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Apply automatic filters (e.g., default study key)."""
        ...

    def _build_path(self, *segments: Any) -> str:
        """Build the API path."""
        ...

    def _require_async_client(self) -> AsyncRequestorProtocol:
        """Return the configured async client or raise if missing."""
        ...
