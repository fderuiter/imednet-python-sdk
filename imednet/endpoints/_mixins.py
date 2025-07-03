from __future__ import annotations

import inspect
import sys
from typing import Any, Dict, List, Optional

from imednet.utils.filters import build_filter_string as default_build_filter_string

from .base import BaseEndpoint


class ListGetEndpointMixin(BaseEndpoint):
    """Shared list/get helpers for endpoints."""

    BASE_PATH = "/api/v1/edc/studies"
    PATH: str
    MODEL: Any
    ID_FIELD: str
    _cache_name: str | None = None
    _pop_study_key: bool = False
    _requires_study_key: bool = False
    _include_study_key_in_filter: bool = False
    _per_study_cache: bool = True
    _page_size: int | None = None
    _param_map: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _build_path(self, study_key: Optional[str], path: str) -> str:
        segments = [self.BASE_PATH.strip("/")]
        if study_key:
            segments.append(str(study_key).strip("/"))
        if path:
            segments.append(path.strip("/"))
        return "/" + "/".join(segments)

    def _parse_item(self, data: Dict[str, Any]) -> Any:
        if hasattr(self.MODEL, "from_json"):
            return self.MODEL.from_json(data)
        return self.MODEL.model_validate(data)

    def _list_impl(
        self,
        client: Any,
        paginator_cls: type[Any],
        *,
        study_key: Optional[str] = None,
        refresh: bool = False,
        **filters: Any,
    ) -> Any:
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        params: Dict[str, Any] = {}
        for key, param in self._param_map.items():
            if key in filters:
                val = filters.pop(key)
                if isinstance(val, bool):
                    val = str(val).lower()
                params[param] = val

        if self._pop_study_key:
            study = filters.pop("studyKey")
            if not study:
                raise ValueError("Study key must be provided or set in the context")
        else:
            study = filters.get("studyKey")
            if self._requires_study_key and not study:
                raise ValueError("Study key must be provided or set in the context")
            if not self._include_study_key_in_filter:
                filters.pop("studyKey", None)

        cache: Any = None
        if self._cache_name:
            cache = getattr(
                self,
                self._cache_name,
                {} if self._per_study_cache else None,
            )
            if not hasattr(self, self._cache_name):
                assert self._cache_name is not None
                setattr(self, self._cache_name, cache)
            if not filters and not refresh:
                if self._per_study_cache:
                    if study in cache:  # type: ignore[operator]
                        return cache[study]  # type: ignore[index]
                else:
                    if cache is not None:
                        return cache

        if filters:
            module = sys.modules[self.__class__.__module__]
            build_filter = getattr(module, "build_filter_string", default_build_filter_string)
            params["filter"] = build_filter(filters)

        paginator_kwargs: Dict[str, Any] = {"params": params}
        if self._page_size is not None:
            paginator_kwargs["page_size"] = self._page_size
        path = self._build_path(study, self.PATH)
        paginator = paginator_cls(client, path, **paginator_kwargs)

        if hasattr(paginator, "__aiter__"):

            async def _collect() -> List[Any]:
                result = [self._parse_item(item) async for item in paginator]
                if cache is not None and not filters:
                    if self._per_study_cache:
                        cache[study] = result  # type: ignore[index]
                    else:
                        assert self._cache_name is not None
                        setattr(self, self._cache_name, result)
                return result

            return _collect()

        result = [self._parse_item(item) for item in paginator]
        if cache is not None and not filters:
            if self._per_study_cache:
                cache[study] = result  # type: ignore[index]
            else:
                assert self._cache_name is not None
                setattr(self, self._cache_name, result)
        return result

    def _get_impl(
        self,
        client: Any,
        paginator_cls: type[Any],
        *,
        study_key: str,
        item_id: Any,
    ) -> Any:
        kwargs = {"study_key": study_key, **{self.ID_FIELD: item_id}}
        if self._cache_name is not None:
            kwargs["refresh"] = True

        result = self._list_impl(client, paginator_cls, **kwargs)

        if inspect.isawaitable(result):

            async def _await() -> Any:
                items = await result
                if not items:
                    raise ValueError(f"{self.ID_FIELD} {item_id} not found in study {study_key}")
                return items[0]

            return _await()

        if not result:
            raise ValueError(f"{self.ID_FIELD} {item_id} not found in study {study_key}")
        return result[0]
