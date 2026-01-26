from __future__ import annotations

import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    cast,
)

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.errors import ResourceNotFound, ValidationError
from imednet.models.json_base import JsonModel
from imednet.utils.filters import build_filter_string

if TYPE_CHECKING:  # pragma: no cover - imported for type hints only

    class _EndpointBase(Protocol):
        def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]: ...
        def _build_path(self, *segments: Any) -> str: ...
        def _require_async_client(self) -> AsyncClient: ...

        PATH: str
        MODEL: Type[JsonModel]
        _id_param: str
        _cache_name: Optional[str]
        requires_study_key: bool
        PAGE_SIZE: int
        _client: Client
        _async_client: Optional[AsyncClient]


T = TypeVar("T", bound=JsonModel)


class EndpointLogicMixin(Generic[T]):
    """Shared logic for endpoint mixins."""

    PATH: str
    MODEL: Type[T]
    _id_param: str
    _cache_name: Optional[str] = None
    requires_study_key: bool = True
    PAGE_SIZE: int = 100
    _pop_study_filter: bool = False
    _missing_study_exception: type[Exception] = ValidationError

    def _parse_item(self, item: Any) -> T:
        if hasattr(self.MODEL, "from_json"):
            return getattr(self.MODEL, "from_json")(item)
        return self.MODEL.model_validate(item)

    def _get_parse_func(self) -> Any:
        # Bolt Optimization: Resolve parsing function once
        if self._parse_item.__func__ is not EndpointLogicMixin._parse_item:  # type: ignore
            return self._parse_item

        parse_func = getattr(self.MODEL, "from_json", None)
        if parse_func is None:
            parse_func = self.MODEL.model_validate
        return parse_func

    def _update_local_cache(
        self,
        result: list[T],
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

    def _prepare_list_request(
        self,
        study_key: Optional[str],
        filters: Dict[str, Any],
        refresh: bool,
        extra_params: Optional[Dict[str, Any]],
    ) -> Tuple[str, Dict[str, Any], Optional[str], Optional[Dict[str, List[T]]]]:
        """
        Prepare parameters for a list request.

        Returns:
            Tuple of (path, query_params, study_key, cache_object)
        """
        # 1. Filter processing
        filters = self._auto_filter(filters)  # type: ignore[attr-defined]
        if study_key:
            filters["studyKey"] = study_key

        study: Optional[str] = None
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
                    raise ValidationError("Study key must be provided or set in the context")
        else:
            study = filters.get("studyKey")

        # 2. Cache Check
        cache = getattr(self, self._cache_name, None) if self._cache_name else None
        other_filters = {k: v for k, v in filters.items() if k != "studyKey"}

        if self.requires_study_key:
            if not study:
                # Should have been caught above, but for safety
                raise ValidationError("Study key must be provided or set in the context")
            if cache is not None and not other_filters and not refresh and study in cache:
                return "", {}, study, cache # Signal cache hit with empty path
        else:
            if cache is not None and not other_filters and not refresh:
                return "", {}, study, cache # Signal cache hit

        # 3. Build Params and Path
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

        path = self._build_path(*segments)  # type: ignore[attr-defined]
        return path, params, study, cache


class SyncListMixin(EndpointLogicMixin[T]):
    """Mixin for synchronous list operations."""

    def _list_sync(
        self,
        client: Client,
        paginator_cls: type[Paginator],
        *,
        study_key: Optional[str] = None,
        refresh: bool = False,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> List[T]:
        path, params, study, cache = self._prepare_list_request(
            study_key, filters, refresh, extra_params
        )

        # Cache hit
        if not path and cache is not None:
             if self.requires_study_key and study:
                 return cache[study]  # type: ignore
             if not self.requires_study_key:
                 return cast(List[T], cache)

        page_size = self.PAGE_SIZE
        paginator = paginator_cls(client, path, params=params, page_size=page_size)
        parse_func = self._get_parse_func()

        result = [parse_func(item) for item in paginator]

        other_filters = {k: v for k, v in filters.items() if k != "studyKey"}
        self._update_local_cache(result, study, bool(other_filters), cache)

        return result

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        """List items synchronously."""
        if hasattr(self, "_list_impl"):
            return self._list_impl(
                self._client,  # type: ignore[attr-defined]
                Paginator,
                study_key=study_key,
                **filters,
            )
        return self._list_sync(
            self._client,  # type: ignore[attr-defined]
            Paginator,
            study_key=study_key,
            **filters,
        )


class AsyncListMixin(EndpointLogicMixin[T]):
    """Mixin for asynchronous list operations."""

    async def _list_async(
        self,
        client: AsyncClient,
        paginator_cls: type[AsyncPaginator],
        *,
        study_key: Optional[str] = None,
        refresh: bool = False,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> List[T]:
        path, params, study, cache = self._prepare_list_request(
            study_key, filters, refresh, extra_params
        )

        # Cache hit
        if not path and cache is not None:
             if self.requires_study_key and study:
                 return cache[study] # type: ignore
             if not self.requires_study_key:
                 return cast(List[T], cache)

        page_size = self.PAGE_SIZE
        paginator = paginator_cls(client, path, params=params, page_size=page_size)
        parse_func = self._get_parse_func()

        result = [parse_func(item) async for item in paginator]

        other_filters = {k: v for k, v in filters.items() if k != "studyKey"}
        self._update_local_cache(result, study, bool(other_filters), cache)

        return result

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        """List items asynchronously."""
        if hasattr(self, "_list_impl"):
            return await self._list_impl(
                self._require_async_client(),  # type: ignore[attr-defined]
                AsyncPaginator,
                study_key=study_key,
                **filters,
            )
        return await self._list_async(
            self._require_async_client(),  # type: ignore[attr-defined]
            AsyncPaginator,
            study_key=study_key,
            **filters,
        )


class SyncGetMixin(SyncListMixin[T]):
    """Mixin for synchronous get operations."""

    def get(self, study_key: Optional[str], item_id: Any) -> T:
        """Get a single item synchronously."""
        filters = {self._id_param: item_id}
        if hasattr(self, "_list_impl"):
            result = self._list_impl(
                self._client,  # type: ignore[attr-defined]
                Paginator,
                study_key=study_key,
                refresh=True,
                **filters,
            )
        else:
            result = self._list_sync(
                self._client,  # type: ignore[attr-defined]
                Paginator,
                study_key=study_key,
                refresh=True,
                **filters,
            )

        if not result:
            if self.requires_study_key:
                raise ResourceNotFound(
                    f"{self.MODEL.__name__} {item_id} not found in study {study_key}"
                )
            raise ResourceNotFound(f"{self.MODEL.__name__} {item_id} not found")
        return result[0]


class AsyncGetMixin(AsyncListMixin[T]):
    """Mixin for asynchronous get operations."""

    async def async_get(self, study_key: Optional[str], item_id: Any) -> T:
        """Get a single item asynchronously."""
        filters = {self._id_param: item_id}
        if hasattr(self, "_list_impl"):
            result = await self._list_impl(
                self._require_async_client(),  # type: ignore[attr-defined]
                AsyncPaginator,
                study_key=study_key,
                refresh=True,
                **filters,
            )
        else:
            result = await self._list_async(
                self._require_async_client(),  # type: ignore[attr-defined]
                AsyncPaginator,
                study_key=study_key,
                refresh=True,
                **filters,
            )

        if not result:
            if self.requires_study_key:
                raise ResourceNotFound(
                    f"{self.MODEL.__name__} {item_id} not found in study {study_key}"
                )
            raise ResourceNotFound(f"{self.MODEL.__name__} {item_id} not found")
        return result[0]


class ListGetEndpointMixin(SyncGetMixin[T], AsyncGetMixin[T]):
    """
    Mixin implementing ``list`` and ``get`` helpers.

    .. deprecated:: 0.4.0
        Use composed mixins instead.
        Kept for backward compatibility with subclasses that call _list_impl.
    """

    def _list_impl(
        self: Any,
        client: Client | AsyncClient,
        paginator_cls: type[Paginator] | type[AsyncPaginator],
        *,
        study_key: Optional[str] = None,
        refresh: bool = False,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> Any:
        """
        Legacy implementation to support existing subclasses that might override or use this.
        Dispatch to _list_sync or _list_async based on client type.
        """
        is_async_client = isinstance(client, AsyncClient)
        is_async_paginator = inspect.isclass(paginator_cls) and issubclass(
            paginator_cls, AsyncPaginator
        )

        if is_async_client or is_async_paginator:
             # Ensure paginator_cls is async compatible (it should be if client is async)
             return self._list_async(
                 cast(AsyncClient, client),
                 cast(Type[AsyncPaginator], paginator_cls),
                 study_key=study_key,
                 refresh=refresh,
                 extra_params=extra_params,
                 **filters
             )
        else:
             return self._list_sync(
                 cast(Client, client),
                 cast(Type[Paginator], paginator_cls),
                 study_key=study_key,
                 refresh=refresh,
                 extra_params=extra_params,
                 **filters
             )


class ListGetEndpoint(BaseEndpoint, ListGetEndpointMixin[T]):
    """Endpoint base class implementing ``list`` and ``get`` helpers."""
    pass
