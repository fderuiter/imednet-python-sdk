from __future__ import annotations

import inspect
import sys
from typing import TYPE_CHECKING, Any, Dict, Iterable, Optional, Protocol, Type

from pydantic import BaseModel

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.utils.filters import build_filter_string

if TYPE_CHECKING:  # pragma: no cover - imported for type hints only

    class _EndpointBase(Protocol):
        def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]: ...
        def _build_path(self, *segments: Any) -> str: ...

        PATH: str
        MODEL: Type[BaseModel]
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
        ) -> Any: ...

        def _parse_item(self, item: Any) -> BaseModel: ...


class ListGetEndpointMixin:
    """Mixin implementing ``list`` and ``get`` helpers."""

    PATH: str
    MODEL: Type[BaseModel]
    _id_param: str
    _cache_name: Optional[str] = None
    requires_study_key: bool = True
    PAGE_SIZE: int = 100
    _pop_study_filter: bool = False
    _missing_study_exception: type[Exception] = ValueError

    def _parse_item(self, item: Any) -> BaseModel:
        if hasattr(self.MODEL, "from_json"):
            return getattr(self.MODEL, "from_json")(item)
        return self.MODEL.model_validate(item)

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

        if hasattr(paginator, "__aiter__"):

            async def _collect() -> list[BaseModel]:
                result = [self._parse_item(item) async for item in paginator]
                if not other_filters:
                    if self.requires_study_key and cache is not None:
                        cache[study] = result
                    elif self._cache_name:
                        setattr(self, self._cache_name, result)
                return result

            return _collect()

        result = [self._parse_item(item) for item in paginator]
        if not other_filters:
            if self.requires_study_key and cache is not None:
                cache[study] = result
            elif self._cache_name:
                setattr(self, self._cache_name, result)
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

            async def _await() -> BaseModel:
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


class ListGetEndpoint(BaseEndpoint, ListGetEndpointMixin):
    """Endpoint base class implementing ``list`` and ``get`` helpers."""

    def _list_common(self, is_async: bool, **kwargs: Any) -> Any:
        client: Client | AsyncClient
        paginator: type[Paginator] | type[AsyncPaginator]
        module = sys.modules[self.__class__.__module__]
        if is_async:
            client = self._require_async_client()
            paginator = getattr(module, "AsyncPaginator")
        else:
            client = self._client
            paginator = getattr(module, "Paginator")
        return self._list_impl(client, paginator, **kwargs)

    def _get_common(
        self,
        is_async: bool,
        *,
        study_key: Optional[str],
        item_id: Any,
    ) -> Any:
        client: Client | AsyncClient
        paginator: type[Paginator] | type[AsyncPaginator]
        module = sys.modules[self.__class__.__module__]
        if is_async:
            client = self._require_async_client()
            paginator = getattr(module, "AsyncPaginator")
        else:
            client = self._client
            paginator = getattr(module, "Paginator")
        return self._get_impl(client, paginator, study_key=study_key, item_id=item_id)

    def list(self, study_key: Optional[str] = None, **filters: Any) -> Any:
        return self._list_common(False, study_key=study_key, **filters)

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> Any:
        return await self._list_common(True, study_key=study_key, **filters)

    def get(self, study_key: Optional[str], item_id: Any) -> Any:
        return self._get_common(False, study_key=study_key, item_id=item_id)

    async def async_get(self, study_key: Optional[str], item_id: Any) -> Any:
        return await self._get_common(True, study_key=study_key, item_id=item_id)
