from typing import Any, Dict, Generic, List, Optional, Protocol, Type, TypeVar, runtime_checkable

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

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Apply automatic filters (e.g., default study key)."""
        ...

    def _build_path(self, *segments: Any) -> str:
        """Build the API path."""
        ...

    def _validate_study_key(self, study_key: Optional[str]) -> None:
        """Validate that a study key is provided if required."""
        ...

    def _get_endpoint_path(self, study_key: Optional[str], *extra_segments: Any) -> str:
        """Build the API path with optional study key and extra segments."""
        ...

    def _raise_not_found(self, study_key: Optional[str], item_id: Any = None) -> None:
        """Raise a standardized NotFoundError."""
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


class SupportsGet(Protocol[T]):
    """Protocol for resources that support ``get`` operations."""

    def get(self, study_key: Optional[str], item_id: Any) -> T:
        """Get a single item synchronously."""
        ...

    async def async_get(self, study_key: Optional[str], item_id: Any) -> T:
        """Get a single item asynchronously."""
        ...


class SupportsList(Protocol[T]):
    """Protocol for resources that support ``list`` operations."""

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        """List items synchronously."""
        ...

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        """List items asynchronously."""
        ...


class SupportsCreate(Protocol[T]):
    """Protocol for resources that support ``create`` operations."""

    def create(self, *args: Any, **kwargs: Any) -> T:
        """Create an item synchronously."""
        ...

    async def async_create(self, *args: Any, **kwargs: Any) -> T:
        """Create an item asynchronously."""
        ...


class SyncOperationProtocol(Protocol, Generic[T]):
    """Protocol for sync operation executors requiring explicit transport injection."""

    def __init__(self, client: RequestorProtocol, path: str, *args: Any, **kwargs: Any) -> None:
        ...

    def execute(self) -> T:
        """Execute synchronously."""
        ...


class AsyncOperationProtocol(Protocol, Generic[T]):
    """Protocol for async operation executors requiring explicit transport injection."""

    def __init__(self, client: AsyncRequestorProtocol, path: str, *args: Any, **kwargs: Any) -> None:
        ...

    async def execute(self) -> T:
        """Execute asynchronously."""
        ...
