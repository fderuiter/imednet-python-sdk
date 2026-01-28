from __future__ import annotations

import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
    cast,
)

from imednet.constants import DEFAULT_PAGE_SIZE
from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.parsing import get_model_parser
from imednet.endpoints.base import BaseEndpoint
from imednet.models.json_base import JsonModel
from imednet.utils.filters import build_filter_string

if TYPE_CHECKING:  # pragma: no cover - imported for type hints only

    class EndpointProtocol(Protocol):
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


T = TypeVar("T", bound=JsonModel)


class ListGetEndpointMixin(Generic[T]):
    """Mixin implementing ``list`` and ``get`` helpers."""

    PATH: str
    MODEL: Type[T]
    _id_param: str
    _cache_name: Optional[str] = None
    requires_study_key: bool = True
    PAGE_SIZE: int = DEFAULT_PAGE_SIZE
    _pop_study_filter: bool = False
    _missing_study_exception: type[Exception] = ValueError

    def _parse_item(self, item: Any) -> T:
        """
        Parse a single item into the model type.

        This method can be overridden by subclasses for custom parsing logic.
        By default, it uses the centralized parsing strategy.

        Args:
            item: Raw data to parse

        Returns:
            Parsed model instance
        """
        parse_func = get_model_parser(self.MODEL)
        return parse_func(item)

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

    def _prepare_list_params(
        self,
        study_key: Optional[str],
        refresh: bool,
        extra_params: Optional[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> tuple[Optional[str], Any, Dict[str, Any], Dict[str, Any]]:
        # This method handles filter normalization and cache retrieval preparation
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
                    raise ValueError("Study key must be provided or set in the context")
        else:
            study = filters.get("studyKey")

        cache = getattr(self, self._cache_name, None) if self._cache_name else None
        other_filters = {k: v for k, v in filters.items() if k != "studyKey"}

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)
        if extra_params:
            params.update(extra_params)

        return study, cache, params, other_filters

    def _get_path(self, study: Optional[str]) -> str:
        segments: Iterable[Any]
        if self.requires_study_key:
            segments = (study, self.PATH)
        else:
            segments = (self.PATH,) if self.PATH else ()
        return self._build_path(*segments)  # type: ignore[attr-defined]

    def _resolve_parse_func(self) -> Callable[[Any], T]:
        """
        Resolve the parsing function to use for this endpoint.

        This optimization resolves the parsing function once to avoid
        repeated attribute lookups in tight loops.

        Returns:
            The parsing function to use
        """
        # Check if _parse_item has been overridden by a subclass
        if self._parse_item.__func__ is not ListGetEndpointMixin._parse_item:  # type: ignore[attr-defined]
            return self._parse_item

        # Use centralized parsing strategy
        return get_model_parser(self.MODEL)

    async def _execute_async_list(
        self,
        paginator: AsyncPaginator,
        parse_func: Callable[[Any], T],
        study: Optional[str],
        has_filters: bool,
        cache: Any,
    ) -> List[T]:
        result = [parse_func(item) async for item in paginator]
        self._update_local_cache(result, study, has_filters, cache)
        return result

    def _execute_sync_list(
        self,
        paginator: Paginator,
        parse_func: Callable[[Any], T],
        study: Optional[str],
        has_filters: bool,
        cache: Any,
    ) -> List[T]:
        result = [parse_func(item) for item in paginator]
        self._update_local_cache(result, study, has_filters, cache)
        return result

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

        study, cache, params, other_filters = self._prepare_list_params(
            study_key, refresh, extra_params, filters
        )

        # Cache Hit Check
        if self.requires_study_key:
            if not study:
                # Should have been caught in _prepare_list_params but strict typing requires check
                raise ValueError("Study key must be provided or set in the context")
            if cache is not None and not other_filters and not refresh and study in cache:
                return cast(List[T], cache[study])
        else:
            if cache is not None and not other_filters and not refresh:
                return cast(List[T], cache)

        path = self._get_path(study)
        paginator = paginator_cls(client, path, params=params, page_size=self.PAGE_SIZE)
        parse_func = self._resolve_parse_func()

        return self._execute_sync_list(paginator, parse_func, study, bool(other_filters), cache)

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

        study, cache, params, other_filters = self._prepare_list_params(
            study_key, refresh, extra_params, filters
        )

        # Cache Hit Check
        if self.requires_study_key:
            if not study:
                # Should have been caught in _prepare_list_params but strict typing requires check
                raise ValueError("Study key must be provided or set in the context")
            if cache is not None and not other_filters and not refresh and study in cache:
                return cast(List[T], cache[study])
        else:
            if cache is not None and not other_filters and not refresh:
                return cast(List[T], cache)

        path = self._get_path(study)
        paginator = paginator_cls(client, path, params=params, page_size=self.PAGE_SIZE)
        parse_func = self._resolve_parse_func()

        return await self._execute_async_list(
            paginator, parse_func, study, bool(other_filters), cache
        )

    def _get_sync(
        self,
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
        self,
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
                raise ValueError(f"{self.MODEL.__name__} {item_id} not found in study {study_key}")
            raise ValueError(f"{self.MODEL.__name__} {item_id} not found")
        return result[0]


class ListGetEndpoint(BaseEndpoint, ListGetEndpointMixin[T]):
    """Endpoint base class implementing ``list`` and ``get`` helpers."""

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        return self._list_sync(
            self._client,
            Paginator,
            study_key=study_key,
            **filters,
        )

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        return await self._list_async(
            self._require_async_client(),
            AsyncPaginator,
            study_key=study_key,
            **filters,
        )

    def get(self, study_key: Optional[str], item_id: Any) -> T:
        return self._get_sync(
            self._client,
            Paginator,
            study_key=study_key,
            item_id=item_id,
        )

    async def async_get(self, study_key: Optional[str], item_id: Any) -> T:
        return await self._get_async(
            self._require_async_client(),
            AsyncPaginator,
            study_key=study_key,
            item_id=item_id,
        )
