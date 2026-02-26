from __future__ import annotations

from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
    runtime_checkable,
)

from httpx import Response

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.models.json_base import JsonModel


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


T = TypeVar("T", bound=JsonModel)
T_RESP = TypeVar("T_RESP")


@runtime_checkable
class ListEndpointProtocol(Protocol[T]):
    """Protocol for endpoints supporting list operations."""

    def _process_list_result(
        self,
        result: List[T],
        study: Optional[str],
        has_filters: bool,
        cache: Any,
    ) -> List[T]:
        """Process the list result (e.g., update cache)."""
        ...


@runtime_checkable
class FilterGetEndpointProtocol(Protocol[T]):
    """Protocol for endpoints supporting get operations via filtering."""

    @property
    def _id_param(self) -> str:
        """The query parameter name for the ID."""
        ...

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
        """Execute synchronous list retrieval."""
        ...

    def _list_async(
        self,
        client: AsyncRequestorProtocol,
        paginator_cls: type[AsyncPaginator],
        *,
        study_key: Optional[str] = None,
        refresh: bool = False,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> Awaitable[List[T]]:
        """Execute asynchronous list retrieval."""
        ...

    def _validate_get_result(self, items: List[T], study_key: Optional[str], item_id: Any) -> T:
        """Validate the result of a get operation."""
        ...


@runtime_checkable
class PathGetEndpointProtocol(Protocol[T]):
    """Protocol for endpoints supporting get operations via direct path."""

    def _get_path_for_id(self, study_key: Optional[str], item_id: Any) -> str:
        """Get the path for a specific item ID."""
        ...

    def _process_response(self, response: Response, study_key: Optional[str], item_id: Any) -> T:
        """Process the response from a direct get request."""
        ...


@runtime_checkable
class CreateEndpointProtocol(Protocol[T_RESP]):
    """Protocol for endpoints supporting create operations."""

    def _prepare_kwargs(
        self,
        json: Any = None,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Prepare keyword arguments for the request."""
        ...

    def _process_response(
        self,
        response: Response,
        parse_func: Optional[Callable[[Any], T_RESP]] = None,
    ) -> T_RESP:
        """Process the response from a create request."""
        ...
