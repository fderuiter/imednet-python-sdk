"""
Protocols defining the interface expected by endpoint mixins.

This module helps decouple mixins from the concrete BaseEndpoint implementation
and avoids circular imports.
"""

from typing import Any, Dict, Optional, Protocol, Type, runtime_checkable

from imednet.core.context import Context
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.models.json_base import JsonModel


@runtime_checkable
class EndpointProtocol(Protocol):
    """Protocol defining the interface required by endpoint mixins."""

    PATH: str
    MODEL: Type[JsonModel]
    _id_param: str
    _cache_name: Optional[str]
    requires_study_key: bool
    PAGE_SIZE: int
    _pop_study_filter: bool
    _missing_study_exception: type[Exception]

    _client: RequestorProtocol
    _async_client: Optional[AsyncRequestorProtocol]
    _ctx: Context

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Inject default filters (e.g., studyKey)."""
        ...

    def _build_path(self, *segments: Any) -> str:
        """Build a full API path from segments."""
        ...

    def _require_async_client(self) -> AsyncRequestorProtocol:
        """Return the async client or raise if missing."""
        ...
