from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from imednet.models.json_base import JsonModel

T = TypeVar("T", bound=JsonModel)


class CacheMixin(Generic[T]):
    """Mixin for handling endpoint caching."""

    requires_study_key: bool
    _enable_cache: bool = False  # Default, overridden by EndpointABC/subclasses
    _cache: Optional[Union[List[T], Dict[str, List[T]]]] = None
    # Default, overridden by GenericEndpoint

    def _get_local_cache(self) -> Optional[Union[List[T], Dict[str, List[T]]]]:
        """
        Retrieve the local cache if caching is enabled.

        Returns:
            The cached data, which can be a list of items or a dictionary mapping
            study keys to lists of items. Returns None if caching is disabled.
        """
        if self._enable_cache:
            return self._cache
        return None

    def _update_local_cache(
        self,
        result: List[T],
        study: str | None,
        has_filters: bool,
    ) -> None:
        """
        Update the local cache with newly fetched results.

        Args:
            result: The newly fetched list of items to cache.
            study: The study key associated with the result, if applicable.
            has_filters: Boolean indicating if the result was filtered (which skips caching).
        """
        if has_filters or not self._enable_cache:
            return

        if self.requires_study_key:
            if isinstance(self._cache, dict) and study is not None:
                self._cache[study] = result
        else:
            self._cache = result

    def _check_cache_hit(
        self,
        study: Optional[str],
        refresh: bool,
        other_filters: Dict[str, Any],
        cache: Optional[Union[List[T], Dict[str, List[T]]]],
    ) -> Optional[List[T]]:
        """
        Check if the requested data is already available in the local cache.

        Args:
            study: The study key being requested.
            refresh: Boolean flag to force a cache refresh.
            other_filters: Additional filters; caching is bypassed if these are present.
            cache: The current cache object to inspect.

        Returns:
            The cached list of items if a valid hit is found; otherwise, None.
        """
        if not self._enable_cache:
            return None

        if self.requires_study_key:
            # Strict check usually done before, but here we just check cache
            if (
                isinstance(cache, dict)
                and study is not None
                and not other_filters
                and not refresh
                and study in cache
            ):
                return cache[study]
        else:
            if isinstance(cache, list) and not other_filters and not refresh:
                return cache
        return None


class CachedEndpointMixin:
    """Mixin that enables caching and sets the default page size for metadata endpoints."""

    _enable_cache: bool = True
    PAGE_SIZE: int = 500
