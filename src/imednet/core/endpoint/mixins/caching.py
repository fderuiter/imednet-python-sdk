from __future__ import annotations

from typing import Any, Dict, Optional


class CacheMixin:
    """Mixin for handling endpoint caching."""

    requires_study_key: bool = True  # Default, can be overridden
    _enable_cache: bool = False  # Default, overridden by EndpointABC/subclasses
    _cache: Any = None  # Default, overridden by GenericEndpoint

    def _get_local_cache(self) -> Any:
        if self._enable_cache:
            return self._cache
        return None

    def _update_local_cache(
        self,
        result: Any,
        study: str | None,
        has_filters: bool,
    ) -> None:
        if has_filters or not self._enable_cache:
            return

        if self.requires_study_key:
            if self._cache is not None:
                self._cache[study] = result
        else:
            self._cache = result

    def _check_cache_hit(
        self,
        study: Optional[str],
        refresh: bool,
        other_filters: Dict[str, Any],
        cache: Any,
    ) -> Optional[Any]:
        if not self._enable_cache:
            return None

        if self.requires_study_key:
            # Strict check usually done before, but here we just check cache
            if cache is not None and not other_filters and not refresh and study in cache:
                return cache[study]
        else:
            if cache is not None and not other_filters and not refresh:
                return cache
        return None

class CachedEndpointMixin:
    """Mixin that enables caching and sets the default page size for metadata endpoints."""
    _enable_cache: bool = True
    PAGE_SIZE: int = 500
