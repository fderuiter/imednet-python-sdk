"""Endpoint mix-ins for shared functionality."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type

from pydantic import BaseModel

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.models._base import JsonModel
from imednet.utils.filters import build_filter_string


class ListGetEndpointMixin:
    """Provide ``list`` and ``get`` helpers for endpoints."""

    PATH: str
    MODEL: Type[JsonModel]
    _id_param: str
    _cache_name: str | None = None
    requires_study_key: bool = True
    PAGE_SIZE: int = 100

    def _parse_item(self, item: Any) -> JsonModel:  # pragma: no cover - simple wrapper
        return self.MODEL.from_json(item)

    if TYPE_CHECKING:

        def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]: ...

        def _build_path(self, *segments: Any) -> str: ...

    def _list_impl(
        self,
        client: Any,
        paginator_cls: type[Paginator] | type[AsyncPaginator],
        *,
        study_key: Optional[str] = None,
        refresh: bool = False,
        **filters: Any,
    ) -> Any:
        filters = self._auto_filter(filters)
        if study_key is not None:
            filters["studyKey"] = study_key

        cache = getattr(self, self._cache_name) if self._cache_name else None
        study = None
        if self.requires_study_key:
            study = filters.pop("studyKey", None)
            if not study:
                raise ValueError("Study key must be provided or set in the context")
            if cache is not None and not filters and not refresh and study in cache:
                return cache[study]
        else:
            if cache is not None and not filters and not refresh:
                return cache

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        if self.requires_study_key:
            path = self._build_path(study, self.PATH)
        else:
            path = self._build_path(self.PATH) if self.PATH else self._build_path()

        paginator = paginator_cls(client, path, params=params, page_size=self.PAGE_SIZE)

        if hasattr(paginator, "__aiter__"):

            async def _collect() -> List[JsonModel]:
                items = [self._parse_item(item) async for item in paginator]
                if self._cache_name and not filters:
                    if self.requires_study_key:
                        cache_dict = cache or {}
                        cache_dict[study] = items
                        setattr(self, self._cache_name, cache_dict)
                    else:
                        setattr(self, self._cache_name, items)
                return items

            return _collect()

        items = [self._parse_item(item) for item in paginator]
        if self._cache_name and not filters:
            if self.requires_study_key:
                cache_dict = cache or {}
                cache_dict[study] = items
                setattr(self, self._cache_name, cache_dict)
            else:
                setattr(self, self._cache_name, items)
        return items

    def _get_impl(
        self,
        client: Any,
        paginator_cls: type[Paginator] | type[AsyncPaginator],
        study_key: Optional[str] = None,
        item_id: Any | None = None,
    ) -> Any:
        if item_id is None:
            item_id = study_key
            study_key = None
        result = self._list_impl(
            client,
            paginator_cls,
            study_key=study_key,
            refresh=True,
            **{self._id_param: item_id},
        )

        if hasattr(result, "__await__"):

            async def _await() -> BaseModel:
                items = await result
                if not items:
                    key = f" in study {study_key}" if study_key else ""
                    raise ValueError(f"{self.MODEL.__name__} {item_id} not found{key}")
                return items[0]

            return _await()

        if not result:
            key = f" in study {study_key}" if study_key else ""
            raise ValueError(f"{self.MODEL.__name__} {item_id} not found{key}")
        return result[0]
