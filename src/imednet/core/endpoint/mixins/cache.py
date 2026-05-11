from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, TypeVar

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.models.json_base import JsonModel

T = TypeVar("T", bound=JsonModel)


class CachedEndpointMixin(Generic[T]):
    """
    Mixin providing local memory caching for endpoint results.
    """

    _cache: Optional[List[T] | Dict[str, List[T]]]  # Pure type annotation

    def _get_local_cache(self) -> Optional[List[T] | Dict[str, List[T]]]:
        if not hasattr(self, "_cache"):
            if getattr(self, "requires_study_key", False):
                self._cache = {}
            else:
                self._cache = None
        return self._cache

    def _update_local_cache(self, result: List[T], study: str | None, has_filters: bool) -> None:
        if has_filters:
            return

        if getattr(self, "requires_study_key", False):
            if not hasattr(self, "_cache") or self._cache is None:
                self._cache = {}
            if isinstance(self._cache, dict) and study is not None:
                self._cache[study] = result
            return

        self._cache = result

    def _check_cache_hit(
        self,
        study: Optional[str],
        refresh: bool,
        has_filters: bool,
        cache: Optional[List[T] | Dict[str, List[T]]],
    ) -> Optional[List[T]]:
        if getattr(self, "requires_study_key", False):
            if (
                isinstance(cache, dict)
                and study is not None
                and not has_filters
                and not refresh
                and study in cache
            ):
                return cache[study]
            return None

        if isinstance(cache, list) and not has_filters and not refresh:
            return cache
        return None

    def _list_sync(
        self,
        client: RequestorProtocol,
        paginator_cls: type[Paginator],
        *,
        study_key: Optional[str] = None,
        refresh: bool = False,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> List[T]:
        # Using super() since this mixin is placed before GenericListGetEndpoint
        state = super()._prepare_list_request(study_key, extra_params, filters)  # type: ignore

        cache = self._get_local_cache()
        cached_result = self._check_cache_hit(state.study, refresh, state.has_filters, cache)

        if cached_result is not None:
            return cached_result

        result = super()._list_sync(  # type: ignore
            client,
            paginator_cls,
            study_key=study_key,
            refresh=refresh,
            extra_params=extra_params,
            **filters,
        )
        self._update_local_cache(result, state.study, state.has_filters)
        return result

    async def _list_async(
        self,
        client: AsyncRequestorProtocol,
        paginator_cls: type[AsyncPaginator],
        *,
        study_key: Optional[str] = None,
        refresh: bool = False,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> List[T]:
        state = super()._prepare_list_request(study_key, extra_params, filters)  # type: ignore

        cache = self._get_local_cache()
        cached_result = self._check_cache_hit(state.study, refresh, state.has_filters, cache)

        if cached_result is not None:
            return cached_result

        result = await super()._list_async(  # type: ignore
            client,
            paginator_cls,
            study_key=study_key,
            refresh=refresh,
            extra_params=extra_params,
            **filters,
        )
        self._update_local_cache(result, state.study, state.has_filters)
        return result
