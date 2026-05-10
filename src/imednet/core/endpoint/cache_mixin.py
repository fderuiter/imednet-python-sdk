"""Mixin for endpoint caching functionality."""

from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, TypeVar

from imednet.models.json_base import JsonModel

T = TypeVar("T", bound=JsonModel)


class CacheMixin(Generic[T]):
    """
    Mixin providing caching logic for endpoints.

    Encapsulates caching state and initialization via lazy initialization
    to avoid leaky abstractions.
    """

    _enable_cache: bool
    requires_study_key: bool
    _cache: Optional[List[T] | Dict[str, List[T]]]

    def _get_local_cache(self) -> Optional[List[T] | Dict[str, List[T]]]:
        if not getattr(self, "_enable_cache", False):
            return None

        # Lazy initialization of the cache
        if not hasattr(self, "_cache") or getattr(self, "_cache", None) is None:
            if getattr(self, "requires_study_key", False):
                self._cache = {}
            else:
                self._cache = None

        return getattr(self, "_cache", None)

    def _update_local_cache(self, result: List[T], study: str | None, has_filters: bool) -> None:
        if has_filters or not getattr(self, "_enable_cache", False):
            return

        if getattr(self, "requires_study_key", False):
            if not hasattr(self, "_cache") or getattr(self, "_cache", None) is None:
                self._cache = {}
            _cache = getattr(self, "_cache", None)
            if isinstance(_cache, dict) and study is not None:
                _cache[study] = result
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
