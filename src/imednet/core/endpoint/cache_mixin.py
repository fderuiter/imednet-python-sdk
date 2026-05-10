"""Mixin for endpoint caching logic."""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from imednet.models.json_base import JsonModel

T = TypeVar("T", bound=JsonModel)


class CachedEndpointMixin(Generic[T]):
    """
    Mixin providing local caching behavior for endpoints.
    """

    requires_study_key: bool

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[call-arg]
        self._cache: Optional[List[T] | Dict[str, List[T]]] = None

    def _get_local_cache(self) -> Optional[List[T] | Dict[str, List[T]]]:
        if getattr(self, "requires_study_key", False) and self._cache is None:
            self._cache = {}
        return self._cache

    def _update_local_cache(self, result: List[T], study: str | None, has_filters: bool) -> None:
        if has_filters:
            return

        if getattr(self, "requires_study_key", False):
            if self._cache is None:
                self._cache = {}
            if isinstance(self._cache, dict) and study is not None:
                self._cache[study] = result
            return

        self._cache = result

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
