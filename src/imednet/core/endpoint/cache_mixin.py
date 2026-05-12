from typing import Any, Dict, Generic, List, Optional, TypeVar

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.models.json_base import JsonModel

T = TypeVar("T", bound=JsonModel)

class CachedEndpointMixin(Generic[T]):
    """
    Mixin that adds caching capabilities to endpoint classes.
    Intercepts _list_sync and _list_async to cache the results.
    """
    _cache_internal: Optional[List[T] | Dict[str, List[T]]] = None

    @property
    def _cache(self) -> List[T] | Dict[str, List[T]]:
        if self._cache_internal is None:
            if getattr(self, "requires_study_key", False):
                self._cache_internal = {}
            else:
                self._cache_internal = []
        return self._cache_internal

    def _get_local_cache(self) -> Optional[List[T] | Dict[str, List[T]]]:
        if getattr(self, "requires_study_key", False) and self._cache_internal is None:
            self._cache_internal = {}
        return self._cache_internal

    def _update_local_cache(self, result: List[T], study: str | None, has_filters: bool) -> None:
        if has_filters:
            return

        if getattr(self, "requires_study_key", False):
            if self._cache_internal is None:
                self._cache_internal = {}
            if isinstance(self._cache_internal, dict) and study is not None:
                self._cache_internal[study] = result
            return

        self._cache_internal = result

    def _check_cache_hit(
        self,
        study: Optional[str],
        refresh: bool,
        other_filters: Dict[str, Any],
        cache: Optional[List[T] | Dict[str, List[T]]],
    ) -> Optional[List[T]]:
        if getattr(self, "requires_study_key", False):
            if (
                isinstance(cache, dict)
                and study is not None
                and not other_filters
                and not refresh
                and study in cache
            ):
                return cache[study]
            return None

        if isinstance(cache, list) and not other_filters and not refresh:
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
        param_state = self._resolve_params(study_key, extra_params, filters) # type: ignore
        study = param_state.study
        other_filters = param_state.other_filters

        cache = self._get_local_cache()
        cached_result = self._check_cache_hit(study, refresh, other_filters, cache)
        if cached_result is not None:
            return cached_result

        result = super()._list_sync( # type: ignore
            client,
            paginator_cls,
            study_key=study_key,
            refresh=refresh,
            extra_params=extra_params,
            **filters,
        )
        self._update_local_cache(result, study, bool(other_filters))
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
        param_state = self._resolve_params(study_key, extra_params, filters) # type: ignore
        study = param_state.study
        other_filters = param_state.other_filters

        cache = self._get_local_cache()
        cached_result = self._check_cache_hit(study, refresh, other_filters, cache)
        if cached_result is not None:
            return cached_result

        result = await super()._list_async( # type: ignore
            client,
            paginator_cls,
            study_key=study_key,
            refresh=refresh,
            extra_params=extra_params,
            **filters,
        )
        self._update_local_cache(result, study, bool(other_filters))
        return result
