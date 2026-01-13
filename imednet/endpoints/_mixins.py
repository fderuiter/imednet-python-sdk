from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Dict, Generic, Iterable, List, Optional, Protocol, Type, TypeVar

from pydantic import BaseModel

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

        PATH: str
        MODEL: Type[JsonModel]
        _id_param: str
        _cache_name: Optional[str]
        requires_study_key: bool
        PAGE_SIZE: int

        def _list_impl(
            self,
            client: Client | AsyncClient,
            paginator_cls: type[Paginator] | type[AsyncPaginator],
            *,
            study_key: Optional[str] | None = None,
            refresh: bool = False,
            extra_params: Optional[Dict[str, Any]] = None,
            **filters: Any,
        ) -> List[JsonModel]: ...

        def _parse_item(self, item: Any) -> JsonModel: ...


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
        # Note: Return type is Any because it could be List[T] or Awaitable[List[T]]
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
                return cache[study]
        else:
            if cache is not None and not other_filters and not refresh and cache is not None:
                return cache

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
        page_size = self.PAGE_SIZE
        paginator = paginator_cls(client, path, params=params, page_size=page_size)

        # Bolt Optimization: Resolve parsing function once to avoid attribute lookup loop overhead
        # We respect overrides of _parse_item if present.
        if self._parse_item.__func__ is not ListGetEndpointMixin._parse_item:
            parse_func = self._parse_item
        else:
            parse_func = getattr(self.MODEL, "from_json", None)
            if parse_func is None:
                parse_func = self.MODEL.model_validate

        if hasattr(paginator, "__aiter__"):

            async def _collect() -> List[T]:
                result = [parse_func(item) async for item in paginator]
                self._update_local_cache(result, study, bool(other_filters), cache)
                return result

            return _collect()

        result = [parse_func(item) for item in paginator]
        self._update_local_cache(result, study, bool(other_filters), cache)
        return result

    def _get_impl(
        self: Any,
        client: Client | AsyncClient,
        paginator_cls: type[Paginator] | type[AsyncPaginator],
        *,
        study_key: Optional[str],
        item_id: Any,
    ) -> Any:
        filters = {self._id_param: item_id}
        result = self._list_impl(
            client,
            paginator_cls,
            study_key=study_key,
            refresh=True,
            **filters,
        )

        if inspect.isawaitable(result):

            async def _await() -> T:
                items = await result
                if not items:
                    if self.requires_study_key:
                        raise ValueError(
                            f"{self.MODEL.__name__} {item_id} not found in study {study_key}"
                        )
                    raise ValueError(f"{self.MODEL.__name__} {item_id} not found")
                return items[0]

            return _await()

        if not result:
            if self.requires_study_key:
                raise ValueError(f"{self.MODEL.__name__} {item_id} not found in study {study_key}")
            raise ValueError(f"{self.MODEL.__name__} {item_id} not found")
        return result[0]


class ListGetEndpoint(BaseEndpoint, ListGetEndpointMixin[T]):
    """Endpoint base class implementing ``list`` and ``get`` helpers."""

    def _get_context(
        self, is_async: bool
    ) -> tuple[Client | AsyncClient, type[Paginator] | type[AsyncPaginator]]:
        if is_async:
            return self._require_async_client(), AsyncPaginator
        return self._client, Paginator

    def _list_common(self, is_async: bool, **kwargs: Any) -> Any:
        client, paginator = self._get_context(is_async)
        return self._list_impl(client, paginator, **kwargs)

    def _get_common(
        self,
        is_async: bool,
        *,
        study_key: Optional[str],
        item_id: Any,
    ) -> Any:
        client, paginator = self._get_context(is_async)
        return self._get_impl(client, paginator, study_key=study_key, item_id=item_id)

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        return self._list_common(False, study_key=study_key, **filters)

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        return await self._list_common(True, study_key=study_key, **filters)

    def get(self, study_key: Optional[str], item_id: Any) -> T:
        return self._get_common(False, study_key=study_key, item_id=item_id)

    async def async_get(self, study_key: Optional[str], item_id: Any) -> T:
        return await self._get_common(True, study_key=study_key, item_id=item_id)
