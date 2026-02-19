from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, List, Optional, Tuple, Union, cast

from imednet.constants import DEFAULT_PAGE_SIZE
from imednet.core.endpoint.abc import EndpointABC
from imednet.core.endpoint.structs import ListRequestState
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.parsing import get_model_parser
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol

from .caching import CacheMixin
from .params import ParamMixin
from .parsing import ParsingMixin, T

if TYPE_CHECKING:
    from imednet.core.protocols import ClientProvider


class ListEndpointMixin(ParamMixin, CacheMixin, ParsingMixin[T], EndpointABC[T]):
    """Mixin implementing ``list`` helpers."""

    PAGE_SIZE: int = DEFAULT_PAGE_SIZE
    PAGINATOR_CLS: type[Paginator] = Paginator
    ASYNC_PAGINATOR_CLS: type[AsyncPaginator] = AsyncPaginator

    def _require_sync_client(self) -> RequestorProtocol:
        """Return the configured sync client."""
        raise NotImplementedError("Mixin must be used in a class providing _require_sync_client")

    def _require_async_client(self) -> AsyncRequestorProtocol:
        """Return the configured async client."""
        raise NotImplementedError("Mixin must be used in a class providing _require_async_client")

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
    ) -> ListRequestState[T]:
        """
        Prepare parameters, cache, and path for list request.

        Returns:
            ListRequestState object containing all necessary context.
        """
        # Resolve parameters using the ParamMixin logic
        param_state = self._resolve_params(study_key, extra_params, filters)
        study = param_state.study
        params = param_state.params
        other_filters = param_state.other_filters

        cache = self._get_local_cache()
        cached_result = self._check_cache_hit(study, refresh, other_filters, cache)

        if cached_result is not None:
            return ListRequestState(
                path="",
                params={},
                study=study,
                has_filters=False,
                cache=None,
                cached_result=cast(List[T], cached_result),
            )

        path = self._get_path(study)
        return ListRequestState(
            path=path,
            params=params,
            study=study,
            has_filters=bool(other_filters),
            cache=cache,
        )

    def _prepare_execution(
        self,
        study_key: Optional[str],
        refresh: bool,
        extra_params: Optional[Dict[str, Any]],
        filters: Dict[str, Any],
        client: RequestorProtocol | AsyncRequestorProtocol,
        paginator_cls: type[Paginator] | type[AsyncPaginator],
    ) -> Union[List[T], Tuple[Any, Callable[[Any], T], Optional[str], bool, Any]]:
        state = self._prepare_list_request(study_key, extra_params, filters, refresh)

        if state.cached_result is not None:
            return state.cached_result

        paginator = paginator_cls(client, state.path, params=state.params, page_size=self.PAGE_SIZE)
        parse_func = self._resolve_parse_func()

        return paginator, parse_func, state.study, state.has_filters, state.cache

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
        result = self._prepare_execution(
            study_key, refresh, extra_params, filters, client, paginator_cls
        )
        if isinstance(result, list):
            return result

        paginator, parse_func, study, has_filters, cache = result
        return self._execute_sync_list(
            cast(Paginator, paginator),
            parse_func,
            study,
            has_filters,
            cache,
        )

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
        result = self._prepare_execution(
            study_key, refresh, extra_params, filters, client, paginator_cls
        )
        if isinstance(result, list):
            return result

        paginator, parse_func, study, has_filters, cache = result
        return await self._execute_async_list(
            cast(AsyncPaginator, paginator),
            parse_func,
            study,
            has_filters,
            cache,
        )

    def list(
        self,
        study_key: Optional[str] = None,
        **filters: Any,
    ) -> List[T]:
        """List items."""
        return self._list_sync(
            self._require_sync_client(),
            self.PAGINATOR_CLS,
            study_key=study_key,
            **filters,
        )

    async def async_list(
        self,
        study_key: Optional[str] = None,
        **filters: Any,
    ) -> List[T]:
        """List items asynchronously."""
        return await self._list_async(
            self._require_async_client(),
            self.ASYNC_PAGINATOR_CLS,
            study_key=study_key,
            **filters,
        )
