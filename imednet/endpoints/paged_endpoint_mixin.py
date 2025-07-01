"""Shared pagination utilities for list/get endpoints."""

from __future__ import annotations

import inspect
from typing import Any, Dict, List, Optional

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.context import Context
from imednet.endpoints.base import BaseEndpoint
from imednet.utils.filters import build_filter_string


class PagedEndpointMixin(BaseEndpoint):
    """Mixin providing paginated ``list``/``get`` helpers with optional caching."""

    MODEL: Any
    PATH_SUFFIX: str | None = None
    ID_FILTER: str
    PAGE_SIZE: int = 100
    CACHE_ENABLED: bool = False
    INCLUDE_STUDY_IN_FILTER: bool = False
    MISSING_STUDY_ERROR: type[Exception] = KeyError

    def __init__(
        self,
        client: Client,
        ctx: Context,
        async_client: AsyncClient | None = None,
    ) -> None:
        super().__init__(client, ctx, async_client)
        self._cache: Any
        if self.CACHE_ENABLED:
            if self.PATH_SUFFIX:
                self._cache = {}
            else:
                self._cache = None

    # ---------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------
    def _parse(self, item: Any) -> Any:
        parser = getattr(self.MODEL, "from_json", None) or getattr(
            self.MODEL, "model_validate", None
        )
        if parser is None:
            raise TypeError("MODEL must provide 'from_json' or 'model_validate'")
        return parser(item)

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
        include_inactive = filters.pop("include_inactive", False)
        record_data_filter = filters.pop("record_data_filter", None)
        if study_key:
            filters["studyKey"] = study_key

        study = None
        if self.PATH_SUFFIX:
            try:
                study = filters.pop("studyKey")
            except KeyError as exc:
                raise self.MISSING_STUDY_ERROR("studyKey") from exc
            if not study:
                raise ValueError("Study key must be provided or set in the context")
            if (
                self.CACHE_ENABLED
                and not filters
                and not refresh
                and study in getattr(self, "_cache", {})
            ):
                return getattr(self, "_cache")[study]
            path = self._build_path(study, self.PATH_SUFFIX)
            if self.INCLUDE_STUDY_IN_FILTER:
                filters_with_study = {**filters, "studyKey": study}
            else:
                filters_with_study = filters
        else:
            if (
                self.CACHE_ENABLED
                and not filters
                and not refresh
                and getattr(self, "_cache", None) is not None
            ):
                return getattr(self, "_cache")
            path = self.PATH
            filters_with_study = filters

        params: Dict[str, Any] = {}
        if filters_with_study:
            params["filter"] = build_filter_string(filters_with_study)
        if record_data_filter is not None:
            params["recordDataFilter"] = record_data_filter
        if include_inactive:
            params["includeInactive"] = str(include_inactive).lower()

        paginator = paginator_cls(client, path, params=params, page_size=self.PAGE_SIZE)

        if hasattr(paginator, "__aiter__"):

            async def _collect() -> List[Any]:
                result = [self._parse(item) async for item in paginator]
                if self.CACHE_ENABLED and not filters:
                    if self.PATH_SUFFIX:
                        getattr(self, "_cache")[study] = result
                    else:
                        setattr(self, "_cache", result)
                return result

            return _collect()

        result = [self._parse(item) for item in paginator]
        if self.CACHE_ENABLED and not filters:
            if self.PATH_SUFFIX:
                getattr(self, "_cache")[study] = result
            else:
                setattr(self, "_cache", result)
        return result

    def _get_impl(
        self,
        client: Any,
        paginator_cls: type[Any],
        identifier: Any,
        *,
        study_key: Optional[str] = None,
    ) -> Any:
        kwargs = {self.ID_FILTER: identifier}
        if self.CACHE_ENABLED:
            kwargs["refresh"] = True
        result = self._list_impl(
            client,
            paginator_cls,
            study_key=study_key,
            **kwargs,
        )

        if inspect.isawaitable(result):

            async def _await() -> Any:
                items = await result
                if not items:
                    if self.PATH_SUFFIX:
                        raise ValueError(
                            f"{self.MODEL.__name__} {identifier} not found in study {study_key}"
                        )
                    raise ValueError(f"{self.MODEL.__name__} {identifier} not found")
                return items[0]

            return _await()

        if not result:
            if self.PATH_SUFFIX:
                raise ValueError(
                    f"{self.MODEL.__name__} {identifier} not found in study {study_key}"
                )
            raise ValueError(f"{self.MODEL.__name__} {identifier} not found")
        return result[0]
