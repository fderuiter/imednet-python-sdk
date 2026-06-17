from typing import (
    Any,
    AsyncIterator,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Protocol,
    Sequence,
    Type,
    TypeVar,
    runtime_checkable,
)

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.models.json_base import JsonModel
from imednet.utils.typing import FilterValue, ItemId

T = TypeVar("T", bound=JsonModel)
T_co = TypeVar("T_co", covariant=True)


@runtime_checkable
class EndpointProtocol(Protocol):
    """Protocol defining the interface for endpoint classes."""

    PATH: str
    MODEL: Type[JsonModel]
    _id_param: str
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

    def _raise_not_found(self, study_key: Optional[str], item_id: Optional[ItemId] = None) -> None:
        """Raise a standardized NotFoundError."""
        ...


@runtime_checkable
class ListEndpointProtocol(Protocol[T]):  # type: ignore[misc]
    """Protocol defining the interface for listing endpoint classes."""

    def _list_sync(
        self,
        client: RequestorProtocol,
        paginator_cls: type[Paginator],
        *,
        study_key: Optional[str] = None,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> Iterator[T]:
        """List items synchronously."""
        ...

    def _list_async(
        self,
        client: AsyncRequestorProtocol,
        paginator_cls: type[AsyncPaginator],
        *,
        study_key: Optional[str] = None,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> AsyncIterator[T]:
        """List items asynchronously."""
        ...


class SupportsGet(Protocol[T_co]):
    """Protocol for resources that support ``get`` operations."""

    def get(self, study_key: Optional[str], item_id: ItemId) -> T_co:
        """Get a single item synchronously."""
        ...

    async def async_get(self, study_key: Optional[str], item_id: ItemId) -> T_co:
        """Get a single item asynchronously."""
        ...


class SupportsList(Protocol[T_co]):
    """Protocol for resources that support ``list`` operations."""

    def list(self, study_key: Optional[str] = None, **filters: FilterValue) -> Iterator[T_co]:
        """List items synchronously."""
        ...

    def async_list(
        self, study_key: Optional[str] = None, **filters: FilterValue
    ) -> AsyncIterator[T_co]:
        """List items asynchronously."""
        ...


class SupportsCreate(Protocol[T_co]):
    """Protocol for resources that support ``create`` operations."""

    def create(self, *args: Any, **kwargs: Any) -> T_co:
        """Create an item synchronously."""
        ...

    async def async_create(self, *args: Any, **kwargs: Any) -> T_co:
        """Create an item asynchronously."""
        ...


class SyncOperationProtocol(Protocol, Generic[T_co]):
    """
    Protocol for sync operation executors requiring explicit transport injection.

    Note:
        These operation protocols are intentionally generic extension points for
        future endpoint operation bindings.
    """

    def __init__(self, client: RequestorProtocol, path: str, *args: Any, **kwargs: Any) -> None: ...

    def execute(self) -> T_co:
        """Execute synchronously."""
        ...


class AsyncOperationProtocol(Protocol, Generic[T_co]):
    """
    Protocol for async operation executors requiring explicit transport injection.

    Note:
        These operation protocols are intentionally generic extension points for
        future endpoint operation bindings.
    """

    def __init__(
        self, client: AsyncRequestorProtocol, path: str, *args: Any, **kwargs: Any
    ) -> None: ...

    async def execute(self) -> T_co:
        """Execute asynchronously."""
        ...
