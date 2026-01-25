from __future__ import annotations

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
    """Mixin implementing shared logic for list/get endpoints."""

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
        else:
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

    def _prepare_list_request(
        self,
        study_key: Optional[str] = None,
        refresh: bool = False,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> Union[List[T], Tuple[str, Dict[str, Any], Optional[str], bool, Any]]:
        """
        Prepare request parameters or return cached result.

        Returns:
            Union[List[T], Tuple[path, params, study_key, has_filters, cache_obj]]
        """
        # Type hinting helper for mixin usage
        self_proto = cast("_EndpointBase", self)

        filters = self_proto._auto_filter(filters)
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

        cache = getattr(self, self._cache_name, None) if self._cache_name else None
        other_filters = {k: v for k, v in filters.items() if k != "studyKey"}

        # Check cache
        if self.requires_study_key:
            if not study:
                 # Should have been caught above, but for type safety
                raise ValueError("Study key must be provided or set in the context")
            if cache is not None and not other_filters and not refresh and study in cache:
                return cache[study]
        else:
            if cache is not None and not other_filters and not refresh and cache is not None:
                return cache # type: ignore[return-value]

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
        path = self_proto._build_path(*segments)

        return path, params, study, bool(other_filters), cache


class SyncListGetMixin(EndpointLogicMixin[T]):
    """Mixin implementing synchronous ``list`` and ``get``."""

    def list(
        self,
        study_key: Optional[str] = None,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any
    ) -> List[T]:
        prepared = self._prepare_list_request(
            study_key=study_key,
            extra_params=extra_params,
            **filters
        )

        if isinstance(prepared, list):
            return prepared

        path, params, study, has_filters, cache = prepared
        self_proto = cast("_EndpointBase", self)

        paginator = Paginator(
            self_proto._client,
            path,
            params=params,
            page_size=self.PAGE_SIZE
        )

        parse_func = self._get_parse_func()
        result = [parse_func(item) for item in paginator]
        self._update_local_cache(result, study, has_filters, cache)
        return result

    def get(self, study_key: Optional[str], item_id: Any) -> T:
        filters = {self._id_param: item_id}
        # Force refresh for get by ID to ensure latest data
        prepared = self._prepare_list_request(study_key=study_key, refresh=True, **filters)

        if isinstance(prepared, list):
             # Should not happen with refresh=True, but handling for type safety
             result = prepared
        else:
            path, params, study, has_filters, cache = prepared
            self_proto = cast("_EndpointBase", self)
            paginator = Paginator(
                self_proto._client,
                path,
                params=params,
                page_size=self.PAGE_SIZE
            )
            parse_func = self._get_parse_func()
            result = [parse_func(item) for item in paginator]
            self._update_local_cache(result, study, has_filters, cache)

        if not result:
            if self.requires_study_key:
                raise ValueError(f"{self.MODEL.__name__} {item_id} not found in study {study_key}")
            raise ValueError(f"{self.MODEL.__name__} {item_id} not found")
        return result[0]


class AsyncListGetMixin(EndpointLogicMixin[T]):
    """Mixin implementing asynchronous ``list`` and ``get``."""

    async def async_list(
        self,
        study_key: Optional[str] = None,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any
    ) -> List[T]:
        prepared = self._prepare_list_request(
            study_key=study_key,
            extra_params=extra_params,
            **filters
        )

        if isinstance(prepared, list):
            return prepared

        path, params, study, has_filters, cache = prepared
        self_proto = cast("_EndpointBase", self)
        client = self_proto._require_async_client()

        paginator = AsyncPaginator(
            client,
            path,
            params=params,
            page_size=self.PAGE_SIZE
        )

        parse_func = self._get_parse_func()
        result = [parse_func(item) async for item in paginator]
        self._update_local_cache(result, study, has_filters, cache)
        return result

    async def async_get(self, study_key: Optional[str], item_id: Any) -> T:
        filters = {self._id_param: item_id}
        prepared = self._prepare_list_request(study_key=study_key, refresh=True, **filters)

        if isinstance(prepared, list):
             result = prepared
        else:
            path, params, study, has_filters, cache = prepared
            self_proto = cast("_EndpointBase", self)
            client = self_proto._require_async_client()

            paginator = AsyncPaginator(
                client,
                path,
                params=params,
                page_size=self.PAGE_SIZE
            )
            parse_func = self._get_parse_func()
            result = [parse_func(item) async for item in paginator]
            self._update_local_cache(result, study, has_filters, cache)

        if not result:
            if self.requires_study_key:
                raise ValueError(f"{self.MODEL.__name__} {item_id} not found in study {study_key}")
            raise ValueError(f"{self.MODEL.__name__} {item_id} not found")
        return result[0]


class ListGetEndpoint(BaseEndpoint, SyncListGetMixin[T], AsyncListGetMixin[T]):
    """Endpoint base class implementing ``list`` and ``get`` helpers."""
    pass
