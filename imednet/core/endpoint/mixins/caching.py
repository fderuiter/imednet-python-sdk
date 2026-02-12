from __future__ import annotations

from typing import Any, Dict, Optional


class CacheMixin:
    """Mixin for handling endpoint caching."""

    _cache_name: Optional[str] = None
    requires_study_key: bool = True  # Default, can be overridden

    def _get_local_cache(self) -> Any:
        if self._cache_name:
            return getattr(self, self._cache_name, None)
        return None

    def _update_local_cache(
        self,
        result: Any,
        study: str | None,
        has_filters: bool,
        cache: Any,
    ) -> None:
        if has_filters:
            return

        if self.requires_study_key and cache is not None:
            cache[study] = result
        elif not self.requires_study_key and self._cache_name:
            setattr(self, self._cache_name, result)

    def _check_cache_hit(
        self,
        study: Optional[str],
        refresh: bool,
        other_filters: Dict[str, Any],
        cache: Any,
    ) -> Optional[Any]:
        if self.requires_study_key:
            # Strict check usually done before, but here we just check cache
            if cache is not None and not other_filters and not refresh and study in cache:
                return cache[study]
        else:
            if cache is not None and not other_filters and not refresh:
                return cache
        return None
