from __future__ import annotations

import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
    cast,
)

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.json_base import JsonModel
from imednet.utils.filters import build_filter_string

if TYPE_CHECKING:  # pragma: no cover - imported for type hints only
    # Protocol to type-hint dependencies expected from the host class
    class EndpointHost(Protocol):
        PATH: str
        MODEL: Type[JsonModel]
        _id_param: str
        _cache_name: Optional[str]
        requires_study_key: bool
        PAGE_SIZE: int
        _pop_study_filter: bool
        _missing_study_exception: type[Exception]

        def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]: ...
        def _build_path(self, *segments: Any) -> str: ...
        def _require_async_client(self) -> AsyncClient: ...

        _client: Client
        _async_client: Optional[AsyncClient]


T = TypeVar("T", bound=JsonModel)


class RequestParams(NamedTuple):
    """Internal container for request parameters."""
    path: str
    params: Dict[str, Any]
    study: Optional[str]
    cache: Optional[Union[Dict[str, List[Any]], List[Any]]]
    other_filters: Dict[str, Any]
    page_size: int


class EndpointLogicMixin(Generic[T]):
    """Shared logic for parameter preparation and caching."""

    PATH: str
    MODEL: Type[T]
    _id_param: str
    _cache_name: Optional[str] = None
    requires_study_key: bool = True
    PAGE_SIZE: int = 100
    _pop_study_filter: bool = False
    _missing_study_exception: type[Exception] = ValueError

    def _parse_item(self, item: Any) -> T:
        if hasattr(self.MODEL, "from_json"):
            return getattr(self.MODEL, "from_json")(item)
        return self.MODEL.model_validate(item)

    def _get_parse_func(self) -> Any:
        # Bolt Optimization: Resolve parsing function once to avoid attribute lookup loop overhead
        # We respect overrides of _parse_item if present.
        if self._parse_item.__func__ is not EndpointLogicMixin._parse_item:  # type: ignore[attr-defined]
            return self._parse_item

        parse_func = getattr(self.MODEL, "from_json", None)
        if parse_func is None:
            parse_func = self.MODEL.model_validate
        return parse_func

    def _update_local_cache(
        self,
        result: List[T],
        study: str | None,
        has_filters: bool,
        cache: Any,
    ) -> None:
        if has_filters:
            return

        if self.requires_study_key and cache is not None:
            cache[study] = result
        elif not self.requires_study_key and self._cache_name:
            setattr(self, self._cache_name, result)

    def _prepare_request(
        self: Any,
        study_key: Optional[str] = None,
        refresh: bool = False,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> Union[List[T], RequestParams]:
        """
        Prepare request parameters or return cached result.

        Returns:
            List[T] if cache hit
            RequestParams if request needed
        """
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        if self.requires_study_key:
            if self._pop_study_filter:
                try:
                    study = filters.pop("studyKey")
                except KeyError as exc:
                    raise self._missing_study_exception(
                        "Study key must be provided or set in the context"
                    ) from exc
            else:
                study = filters.get("studyKey")
                if not study:
                    raise ValueError("Study key must be provided or set in the context")
        else:
            study = filters.get("studyKey")

        cache = getattr(self, self._cache_name, None) if self._cache_name else None
        other_filters = {k: v for k, v in filters.items() if k != "studyKey"}

        if self.requires_study_key:
            if not study:
                raise ValueError("Study key must be provided or set in the context")
            if cache is not None and not other_filters and not refresh and study in cache:
                return cast(List[T], cache[study])
        else:
            if cache is not None and not other_filters and not refresh and cache is not None:
                return cast(List[T], cache)

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)
        if extra_params:
            params.update(extra_params)

        segments: Iterable[Any]
        if self.requires_study_key:
            segments = (study, self.PATH)
        else:
            segments = (self.PATH,) if self.PATH else ()

        path = self._build_path(*segments)

        return RequestParams(
            path=path,
            params=params,
            study=study,
            cache=cache,
            other_filters=other_filters,
            page_size=self.PAGE_SIZE,
        )


class SyncListMixin(EndpointLogicMixin[T]):
    """Mixin implementing synchronous ``list``."""

    _client: Client

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        result_or_params = self._prepare_request(study_key=study_key, **filters)

        if isinstance(result_or_params, list):
            return result_or_params

        rp = result_or_params
        paginator = Paginator(
            self._client,
            rp.path,
            params=rp.params,
            page_size=rp.page_size
        )

        parse_func = self._get_parse_func()
        result = [parse_func(item) for item in paginator]

        self._update_local_cache(result, rp.study, bool(rp.other_filters), rp.cache)
        return result


class AsyncListMixin(EndpointLogicMixin[T]):
    """Mixin implementing asynchronous ``async_list``."""

    def _require_async_client(self) -> AsyncClient: ...

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        result_or_params = self._prepare_request(study_key=study_key, **filters)

        if isinstance(result_or_params, list):
            return result_or_params

        rp = result_or_params
        client = self._require_async_client()
        paginator = AsyncPaginator(
            client,
            rp.path,
            params=rp.params,
            page_size=rp.page_size
        )

        parse_func = self._get_parse_func()
        result = [parse_func(item) async for item in paginator]

        self._update_local_cache(result, rp.study, bool(rp.other_filters), rp.cache)
        return result


class SyncGetMixin(SyncListMixin[T]):
    """Mixin implementing synchronous ``get``."""

    def get(self, study_key: Optional[str], item_id: Any) -> T:
        filters = {self._id_param: item_id}
        # Force refresh to bypass cache for specific item retrieval
        # Note: We reuse _prepare_request logic by calling it directly or via list but with refresh=True
        # However, calling self.list(..., refresh=True) is not directly exposed.
        # So we manually invoke _prepare_request with refresh=True logic.

        # Re-using list implementation logic but forcing refresh
        result_or_params = self._prepare_request(
            study_key=study_key,
            refresh=True,
            **filters
        )

        if isinstance(result_or_params, list):
            # Should not happen with refresh=True
            return result_or_params[0]

        rp = result_or_params
        paginator = Paginator(
            self._client,
            rp.path,
            params=rp.params,
            page_size=rp.page_size
        )

        parse_func = self._get_parse_func()
        # We only expect one item
        items = [parse_func(item) for item in paginator]

        if not items:
            if self.requires_study_key:
                raise ValueError(f"{self.MODEL.__name__} {item_id} not found in study {study_key}")
            raise ValueError(f"{self.MODEL.__name__} {item_id} not found")

        return items[0]


class AsyncGetMixin(AsyncListMixin[T]):
    """Mixin implementing asynchronous ``async_get``."""

    async def async_get(self, study_key: Optional[str], item_id: Any) -> T:
        filters = {self._id_param: item_id}
        result_or_params = self._prepare_request(
            study_key=study_key,
            refresh=True,
            **filters
        )

        if isinstance(result_or_params, list):
            return result_or_params[0]

        rp = result_or_params
        client = self._require_async_client()
        paginator = AsyncPaginator(
            client,
            rp.path,
            params=rp.params,
            page_size=rp.page_size
        )

        parse_func = self._get_parse_func()
        items = [parse_func(item) async for item in paginator]

        if not items:
            if self.requires_study_key:
                raise ValueError(f"{self.MODEL.__name__} {item_id} not found in study {study_key}")
            raise ValueError(f"{self.MODEL.__name__} {item_id} not found")

        return items[0]


# Helper to maintain backward compatibility for direct imports if any
ListGetEndpointMixin = EndpointLogicMixin


class ListGetEndpoint(
    BaseEndpoint,
    SyncGetMixin[T],
    AsyncGetMixin[T],
):
    """Endpoint base class implementing ``list`` and ``get`` helpers."""

    pass
