from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, cast

from imednet.constants import DEFAULT_PAGE_SIZE
from imednet.core.endpoint.abc import EndpointABC
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.parsing import get_model_parser
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol

from .caching import CacheMixin
from .params import ParamMixin
from .parsing import ParsingMixin, T


class ListEndpointMixin(ParamMixin, CacheMixin, ParsingMixin[T], EndpointABC[T]):
    """Mixin implementing ``list`` helpers."""

    PAGE_SIZE: int = DEFAULT_PAGE_SIZE

    def _get_path(self, study: Optional[str]) -> str:
        segments: Iterable[Any]
        if self.requires_study_key:
            segments = (study, self.PATH)
        else:
            segments = (self.PATH,) if self.PATH else ()
        return self._build_path(*segments)

    def _resolve_parse_func(self) -> Callable[[Any], T]:
        """
        Resolve the parsing function to use for this endpoint.

        This optimization resolves the parsing function once to avoid
        repeated attribute lookups in tight loops.

        Returns:
            The parsing function to use
        """
        # Check if _parse_item has been overridden by a subclass
        # We check against ParsingMixin which provides the default implementation
        if self._parse_item.__func__ is not ParsingMixin._parse_item:  # type: ignore[attr-defined]
            return self._parse_item

        # Use centralized parsing strategy
        return get_model_parser(self.MODEL)

    def _process_list_result(
        self,
        result: List[T],
        study: Optional[str],
        has_filters: bool,
        cache: Any,
    ) -> List[T]:
        self._update_local_cache(result, study, has_filters, cache)
        return result

    async def _execute_async_list(
        self,
        paginator: AsyncPaginator,
        parse_func: Callable[[Any], T],
        study: Optional[str],
        has_filters: bool,
        cache: Any,
    ) -> List[T]:
        result = [parse_func(item) async for item in paginator]
        return self._process_list_result(result, study, has_filters, cache)

    def _execute_sync_list(
        self,
        paginator: Paginator,
        parse_func: Callable[[Any], T],
        study: Optional[str],
        has_filters: bool,
        cache: Any,
    ) -> List[T]:
        result = [parse_func(item) for item in paginator]
        return self._process_list_result(result, study, has_filters, cache)

    def _prepare_list_request(
        self,
        study_key: Optional[str],
        extra_params: Optional[Dict[str, Any]],
        filters: Dict[str, Any],
        refresh: bool,
    ) -> tuple[Optional[List[T]], str, Dict[str, Any], Optional[str], bool, Any]:
        """
        Prepare parameters, cache, and path for list request.

        Returns:
            Tuple of (cached_result, path, params, study, has_other_filters, cache_obj)
        """
        # self is ListEndpointMixin, which inherits ParamMixin and CacheMixin
        study, params, other_filters = self._resolve_params(study_key, extra_params, filters)

        cache = self._get_local_cache()
        cached_result = self._check_cache_hit(study, refresh, other_filters, cache)

        if cached_result is not None:
            return cast(List[T], cached_result), "", {}, study, False, None

        path = self._get_path(study)
        return None, path, params, study, bool(other_filters), cache

    def _list_impl(
        self,
        client: RequestorProtocol | AsyncRequestorProtocol,
        paginator_cls: type[Paginator] | type[AsyncPaginator],
        *,
        study_key: Optional[str] = None,
        refresh: bool = False,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> List[T] | Awaitable[List[T]]:

        cached_result, path, params, study, has_filters, cache = self._prepare_list_request(
            study_key, extra_params, filters, refresh
        )

        if cached_result is not None:
            return cached_result

        paginator = paginator_cls(client, path, params=params, page_size=self.PAGE_SIZE)
        parse_func = self._resolve_parse_func()

        if hasattr(paginator, "__aiter__"):
            return self._execute_async_list(
                cast(AsyncPaginator, paginator), parse_func, study, has_filters, cache
            )

        return self._execute_sync_list(
            cast(Paginator, paginator), parse_func, study, has_filters, cache
        )
