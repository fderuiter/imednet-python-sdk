from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")

class CachedEndpointMixin(Generic[T]):
    """
    Mixin providing caching functionality for endpoints.

    Manages cache state and lazy initialization to keep base classes
    agnostic of caching details.
    """

    _enable_cache: bool
    _cache: Optional[List[T] | Dict[str, List[T]]]
    requires_study_key: bool

    def _get_local_cache(self) -> Optional[List[T] | Dict[str, List[T]]]:
        if not getattr(self, "_enable_cache", False):
            return None

        if getattr(self, "requires_study_key", True) and getattr(self, "_cache", None) is None:
            self._cache = {}
        return getattr(self, "_cache", None)

    def _update_local_cache(self, result: List[T], study: str | None, has_filters: bool) -> None:
        if has_filters or not getattr(self, "_enable_cache", False):
            return

        if getattr(self, "requires_study_key", True):
            if getattr(self, "_cache", None) is None:
                self._cache = {}
            if isinstance(getattr(self, "_cache", None), dict) and study is not None:
                self._cache[study] = result  # type: ignore
            return

        self._cache = result

    def _check_cache_hit(
        self,
        study: Optional[str],
        refresh: bool,
        other_filters: Dict[str, Any],
        cache: Optional[List[T] | Dict[str, List[T]]],
    ) -> Optional[List[T]]:
        if not getattr(self, "_enable_cache", False):
            return None

        if getattr(self, "requires_study_key", True):
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
