from typing import Any, Dict, List, Optional, Protocol, Type, TypeVar, runtime_checkable

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.models.json_base import JsonModel

T = TypeVar("T", bound=JsonModel)


@runtime_checkable
class EndpointProtocol(Protocol):
    """Protocol defining the interface for endpoint classes."""

    PATH: str
    MODEL: Type[JsonModel]
    _id_param: str
    _enable_cache: bool
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


@runtime_checkable
class ListEndpointProtocol(Protocol[T]):
    """Protocol defining the interface for listing endpoint classes."""

    def _list_sync(
        self,
        client: RequestorProtocol,
        paginator_cls: type[Paginator],
        *,
        study_key: Optional[str] = None,
        refresh: bool = False,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> List[T]:
        """List items synchronously."""
        ...

    async def _list_async(
        self,
        client: AsyncRequestorProtocol,
        paginator_cls: type[AsyncPaginator],
        *,
        study_key: Optional[str] = None,
        refresh: bool = False,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> List[T]:
        """List items asynchronously."""
        ...
