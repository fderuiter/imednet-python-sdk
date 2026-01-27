from __future__ import annotations

import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
)

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
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


T = TypeVar("T", bound=JsonModel)


class ListGetEndpointMixin(Generic[T]):
    """Mixin implementing ``list`` and ``get`` helpers."""

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

    def _get_parse_func(self) -> Callable[[Any], T]:
        # Bolt Optimization: Resolve parsing function once to avoid attribute lookup loop overhead
        # We respect overrides of _parse_item if present.
        if self._parse_item.__func__ is not ListGetEndpointMixin._parse_item:  # type: ignore
            return self._parse_item

        parse_func = getattr(self.MODEL, "from_json", None)
        if parse_func is None:
            return self.MODEL.model_validate  # type: ignore
        return parse_func

    def _process_filters(self, filters: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Process filters and return (standard_filters, extra_params).
        Subclasses can override this to extract specific filters into extra_params.
        """
        return filters, {}

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

    def _prepare_execution(
        self: Any,
        study_key: Optional[str],
        refresh: bool,
        filters: Dict[str, Any],
    ) -> tuple[Optional[List[T]], str, Dict[str, Any], Optional[str], Any, bool]:
        """
        Prepare for execution by validating inputs, checking cache, and building params/path.
        Returns: (cached_result, path, params, study_key, cache_object, has_filters)
        """
        filters = self._auto_filter(filters)
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
                    raise ValueError("Study key must be provided or set in the context")
        else:
            study = filters.get("studyKey")

        # Process filters to extract extra params
        filters, extra_params = self._process_filters(filters)

        cache = getattr(self, self._cache_name, None) if self._cache_name else None
        other_filters = {k: v for k, v in filters.items() if k != "studyKey"}
        has_filters = bool(other_filters)

        # Check cache
        cached_result = None
        if self.requires_study_key:
            if not study:
                raise ValueError("Study key must be provided or set in the context")
            if cache is not None and not has_filters and not refresh and study in cache:
                cached_result = cache[study]
        else:
            if cache is not None and not has_filters and not refresh:
                cached_result = cache

        if cached_result is not None:
            return cached_result, "", {}, study, cache, has_filters

        # Build params
        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)
        if extra_params:
            params.update(extra_params)

        # Build path
        segments: Iterable[Any]
        if self.requires_study_key:
            segments = (study, self.PATH)
        else:
            segments = (self.PATH,) if self.PATH else ()
        path = self._build_path(*segments)

        return None, path, params, study, cache, has_filters

    def _list_sync(
        self: Any,
        client: Client,
        paginator_cls: type[Paginator],
        *,
        study_key: Optional[str] = None,
        refresh: bool = False,
        **filters: Any,
    ) -> List[T]:
        cached, path, params, study, cache, has_filters = self._prepare_execution(
            study_key, refresh, filters
        )
        if cached is not None:
            return cached

        page_size = self.PAGE_SIZE
        paginator = paginator_cls(client, path, params=params, page_size=page_size)
        parse_func = self._get_parse_func()

        result = [parse_func(item) for item in paginator]

        self._update_local_cache(result, study, has_filters, cache)
        return result

    async def _list_async(
        self: Any,
        client: AsyncClient,
        paginator_cls: type[AsyncPaginator],
        *,
        study_key: Optional[str] = None,
        refresh: bool = False,
        **filters: Any,
    ) -> List[T]:
        cached, path, params, study, cache, has_filters = self._prepare_execution(
            study_key, refresh, filters
        )
        if cached is not None:
            return cached

        page_size = self.PAGE_SIZE
        paginator = paginator_cls(client, path, params=params, page_size=page_size)
        parse_func = self._get_parse_func()

        result = [parse_func(item) async for item in paginator]

        self._update_local_cache(result, study, has_filters, cache)
        return result

    def _get_sync(
        self: Any,
        client: Client,
        paginator_cls: type[Paginator],
        *,
        study_key: Optional[str],
        item_id: Any,
    ) -> T:
        filters = {self._id_param: item_id}
        result = self._list_sync(
            client,
            paginator_cls,
            study_key=study_key,
            refresh=True,
            **filters,
        )

        if not result:
            if self.requires_study_key:
                raise ValueError(f"{self.MODEL.__name__} {item_id} not found in study {study_key}")
            raise ValueError(f"{self.MODEL.__name__} {item_id} not found")
        return result[0]

    async def _get_async(
        self: Any,
        client: AsyncClient,
        paginator_cls: type[AsyncPaginator],
        *,
        study_key: Optional[str],
        item_id: Any,
    ) -> T:
        filters = {self._id_param: item_id}
        result = await self._list_async(
            client,
            paginator_cls,
            study_key=study_key,
            refresh=True,
            **filters,
        )

        if not result:
            if self.requires_study_key:
                raise ValueError(
                    f"{self.MODEL.__name__} {item_id} not found in study {study_key}"
                )
            raise ValueError(f"{self.MODEL.__name__} {item_id} not found")
        return result[0]


class ListGetEndpoint(BaseEndpoint, ListGetEndpointMixin[T]):
    """Endpoint base class implementing ``list`` and ``get`` helpers."""

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        return self._list_sync(self._client, Paginator, study_key=study_key, **filters)

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        client = self._require_async_client()
        return await self._list_async(client, AsyncPaginator, study_key=study_key, **filters)

    def get(self, study_key: Optional[str], item_id: Any) -> T:
        return self._get_sync(self._client, Paginator, study_key=study_key, item_id=item_id)

    async def async_get(self, study_key: Optional[str], item_id: Any) -> T:
        client = self._require_async_client()
        return await self._get_async(client, AsyncPaginator, study_key=study_key, item_id=item_id)
