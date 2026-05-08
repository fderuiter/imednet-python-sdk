from typing import Any, Dict, Generic, List, Optional, TypeVar

from imednet.models.json_base import JsonModel

T = TypeVar("T", bound=JsonModel)


class CacheMixin(Generic[T]):
    """
    Mixin that encapsulates caching state and logic for endpoints.
    """

    _enable_cache: bool
    requires_study_key: bool
    _cache: Optional[List[T] | Dict[str, List[T]]]

    def _get_local_cache(self) -> Optional[List[T] | Dict[str, List[T]]]:
        if not self._enable_cache:
            return None

        if not hasattr(self, "_cache"):
            self._cache = None

        if self.requires_study_key and self._cache is None:
            self._cache = {}

        return self._cache

    def _update_local_cache(self, result: List[T], study: str | None, has_filters: bool) -> None:
        if has_filters or not self._enable_cache:
            return

        if self.requires_study_key:
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
        other_filters: Dict[str, Any],
        cache: Optional[List[T] | Dict[str, List[T]]],
    ) -> Optional[List[T]]:
        if not self._enable_cache:
            return None

        if self.requires_study_key:
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
