from __future__ import annotations

import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Type,
    TypeVar,
    cast,
)

from imednet.constants import DEFAULT_PAGE_SIZE
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.parsing import get_model_parser
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.models.json_base import JsonModel
from imednet.utils.filters import build_filter_string

from .base import BaseEndpoint
from .protocols import EndpointProtocol

if TYPE_CHECKING:  # pragma: no cover
    # EndpointProtocol is imported from .protocols, but we keep this import for
    # backward compatibility if needed
    pass


T = TypeVar("T", bound=JsonModel)


class ParsingMixin(Generic[T]):
    """Mixin implementing model parsing helpers."""

    MODEL: Type[T]

    def _parse_item(self, item: Any) -> T:
        """
        Parse a single item into the model type.

        This method can be overridden by subclasses for custom parsing logic.
        By default, it uses the centralized parsing strategy.

        Args:
            item: Raw data to parse

        Returns:
            Parsed model instance
        """
        parse_func = get_model_parser(self.MODEL)
        return parse_func(item)


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


class ParamMixin:
    """Mixin for handling endpoint parameters and filters."""

    requires_study_key: bool = True
    _pop_study_filter: bool = False
    _missing_study_exception: type[Exception] = ValueError

    def _extract_special_params(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hook to extract special parameters from filters.

        Subclasses should override this method to handle parameters that need to be
        passed separately (e.g. in extra_params) rather than in the filter string.
        These parameters should be removed from the filters dictionary.
        """
        return {}

    def _resolve_params(
        self,
        study_key: Optional[str],
        extra_params: Optional[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> tuple[Optional[str], Dict[str, Any], Dict[str, Any]]:
        # This method handles filter normalization and cache retrieval preparation
        # Assuming _auto_filter is available via self (EndpointProtocol)
        filters = cast(EndpointProtocol, self)._auto_filter(filters)

        # Extract special parameters using the hook
        special_params = self._extract_special_params(filters)

        if special_params:
            if extra_params is None:
                extra_params = {}
            extra_params.update(special_params)

        if study_key:
            filters["studyKey"] = study_key

        study: Optional[str] = None
        if self.requires_study_key:
            if self._pop_study_filter:
                try:
                    study = filters.pop("studyKey")
                except KeyError as exc:
                    raise self._missing_study_exception(
                        "Study key must be provided or set in the context"
                    ) from exc
            else:
                study = filters.get("studyKey")
                if not study:
                    raise ValueError("Study key must be provided or set in the context")
        else:
            study = filters.get("studyKey")

        other_filters = {k: v for k, v in filters.items() if k != "studyKey"}

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)
        if extra_params:
            params.update(extra_params)

        return study, params, other_filters


class ListEndpointMixin(ParamMixin, CacheMixin, ParsingMixin[T]):
    """Mixin implementing ``list`` helpers."""

    PATH: str
    PAGE_SIZE: int = DEFAULT_PAGE_SIZE

    def _get_path(self, study: Optional[str]) -> str:
        # Cast to EndpointProtocol to access PATH and _build_path
        protocol_self = cast(EndpointProtocol, self)
        segments: Iterable[Any]
        if protocol_self.requires_study_key:
            segments = (study, protocol_self.PATH)
        else:
            segments = (protocol_self.PATH,) if protocol_self.PATH else ()
        return protocol_self._build_path(*segments)

    def _resolve_parse_func(self) -> Callable[[Any], T]:
        """
        Resolve the parsing function to use for this endpoint.

        This optimization resolves the parsing function once to avoid
        repeated attribute lookups in tight loops.

        Returns:
            The parsing function to use
        """
        # Check if _parse_item has been overridden by a subclass
        if self._parse_item.__func__ is not ListEndpointMixin._parse_item:  # type: ignore[attr-defined]
            return self._parse_item

        # Use centralized parsing strategy
        return get_model_parser(self.MODEL)

    async def _execute_async_list(
        self,
        paginator: AsyncPaginator,
        parse_func: Callable[[Any], T],
        study: Optional[str],
        has_filters: bool,
        cache: Any,
    ) -> List[T]:
        result = [parse_func(item) async for item in paginator]
        self._update_local_cache(result, study, has_filters, cache)
        return result

    def _execute_sync_list(
        self,
        paginator: Paginator,
        parse_func: Callable[[Any], T],
        study: Optional[str],
        has_filters: bool,
        cache: Any,
    ) -> List[T]:
        result = [parse_func(item) for item in paginator]
        self._update_local_cache(result, study, has_filters, cache)
        return result

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


class FilterGetEndpointMixin(Generic[T]):
    """Mixin implementing ``get`` via filtering."""

    MODEL: Type[T]
    _id_param: str
    requires_study_key: bool = True

    # This should be provided by ListEndpointMixin
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
        raise NotImplementedError

    def _get_impl(
        self,
        client: RequestorProtocol | AsyncRequestorProtocol,
        paginator_cls: type[Paginator] | type[AsyncPaginator],
        *,
        study_key: Optional[str],
        item_id: Any,
    ) -> T | Awaitable[T]:
        filters = {self._id_param: item_id}
        result = self._list_impl(
            client,
            paginator_cls,
            study_key=study_key,
            refresh=True,
            **filters,
        )

        if inspect.isawaitable(result):

            async def _await() -> T:
                items = await result
                if not items:
                    if self.requires_study_key:
                        raise ValueError(
                            f"{self.MODEL.__name__} {item_id} not found in study {study_key}"
                        )
                    raise ValueError(f"{self.MODEL.__name__} {item_id} not found")
                return items[0]

            return _await()

        # Sync path
        items = cast(List[T], result)
        if not items:
            if self.requires_study_key:
                raise ValueError(f"{self.MODEL.__name__} {item_id} not found in study {study_key}")
            raise ValueError(f"{self.MODEL.__name__} {item_id} not found")
        return items[0]


class PathGetEndpointMixin(ParsingMixin[T]):
    """Mixin implementing ``get`` via direct path."""

    PATH: str
    requires_study_key: bool = True

    def _build_path(self, *segments: Any) -> str:
        # Expected from BaseEndpoint
        raise NotImplementedError

    def _get_path_for_id(self, study_key: Optional[str], item_id: Any) -> str:
        segments: Iterable[Any]
        if self.requires_study_key:
            if not study_key:
                raise ValueError("Study key must be provided")
            segments = (study_key, self.PATH, item_id)
        else:
            segments = (self.PATH, item_id) if self.PATH else (item_id,)
        # self is mixed into BaseEndpoint which implements _build_path
        # Use cast for type checking compliance without importing BaseEndpoint
        return cast(BaseEndpoint, self)._build_path(*segments)

    def _raise_not_found(self, study_key: Optional[str], item_id: Any) -> None:
        raise ValueError(f"{self.MODEL.__name__} not found")

    def _get_impl_path(
        self,
        client: RequestorProtocol | AsyncRequestorProtocol,
        *,
        study_key: Optional[str],
        item_id: Any,
        is_async: bool = False,
    ) -> T | Awaitable[T]:
        path = self._get_path_for_id(study_key, item_id)

        # Helper to process response
        def process_response(response: Any) -> T:
            data = response.json()
            if not data:
                # Enforce strict validation for empty body
                self._raise_not_found(study_key, item_id)
            return self._parse_item(data)

        if is_async:

            async def _await() -> T:
                # We assume client is AsyncRequestorProtocol because is_async=True
                # But we can't be sure type-wise unless we narrow it down.
                # In practice, caller ensures this.
                aclient = cast(AsyncRequestorProtocol, client)
                response = await aclient.get(path)
                return process_response(response)

            return _await()

        sclient = cast(RequestorProtocol, client)
        response = sclient.get(path)
        return process_response(response)


class ListGetEndpointMixin(ListEndpointMixin[T], FilterGetEndpointMixin[T]):
    """Mixin implementing ``list`` and ``get`` helpers."""

    pass


class ListEndpoint(BaseEndpoint, ListEndpointMixin[T]):
    """Endpoint base class implementing ``list`` helpers."""

    PAGINATOR_CLS: type[Paginator] = Paginator
    ASYNC_PAGINATOR_CLS: type[AsyncPaginator] = AsyncPaginator

    def _get_context(
        self, is_async: bool
    ) -> tuple[RequestorProtocol | AsyncRequestorProtocol, type[Paginator] | type[AsyncPaginator]]:
        if is_async:
            return self._require_async_client(), self.ASYNC_PAGINATOR_CLS
        return self._client, self.PAGINATOR_CLS

    def _list_common(self, is_async: bool, **kwargs: Any) -> List[T] | Awaitable[List[T]]:
        client, paginator = self._get_context(is_async)
        return self._list_impl(client, paginator, **kwargs)

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        return cast(List[T], self._list_common(False, study_key=study_key, **filters))

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        return await cast(
            Awaitable[List[T]], self._list_common(True, study_key=study_key, **filters)
        )


class ListGetEndpoint(ListEndpoint[T], FilterGetEndpointMixin[T]):
    """Endpoint base class implementing ``list`` and ``get`` helpers."""

    def _get_common(
        self,
        is_async: bool,
        *,
        study_key: Optional[str],
        item_id: Any,
    ) -> T | Awaitable[T]:
        client, paginator = self._get_context(is_async)
        return self._get_impl(client, paginator, study_key=study_key, item_id=item_id)

    def get(self, study_key: Optional[str], item_id: Any) -> T:
        return cast(T, self._get_common(False, study_key=study_key, item_id=item_id))

    async def async_get(self, study_key: Optional[str], item_id: Any) -> T:
        return await cast(
            Awaitable[T], self._get_common(True, study_key=study_key, item_id=item_id)
        )


class ListPathGetEndpoint(ListEndpoint[T], PathGetEndpointMixin[T]):
    """Endpoint base class implementing ``list`` and ``get`` (via path) helpers."""

    def get(self, study_key: Optional[str], item_id: Any) -> T:
        return cast(T, self._get_impl_path(self._client, study_key=study_key, item_id=item_id))

    async def async_get(self, study_key: Optional[str], item_id: Any) -> T:
        client = self._require_async_client()
        return await cast(
            Awaitable[T],
            self._get_impl_path(client, study_key=study_key, item_id=item_id, is_async=True),
        )


T_RESP = TypeVar("T_RESP")


class CreateEndpointMixin(Generic[T_RESP]):
    """Mixin implementing creation logic."""

    def _create_impl(
        self,
        client: RequestorProtocol | AsyncRequestorProtocol,
        path: str,
        *,
        json: Any = None,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        parse_func: Optional[Callable[[Any], T_RESP]] = None,
    ) -> T_RESP | Awaitable[T_RESP]:
        """
        Execute a creation request (POST).

        Handles both sync and async execution based on the client type.
        """

        def process_response(response: Any) -> T_RESP:
            payload = response.json()
            if parse_func:
                return parse_func(payload)
            return cast(T_RESP, payload)

        # Prepare kwargs to filter out None values to preserve default behavior
        kwargs: Dict[str, Any] = {}
        if json is not None:
            kwargs["json"] = json
        if data is not None:
            kwargs["data"] = data
        if headers is not None:
            kwargs["headers"] = headers

        if inspect.iscoroutinefunction(client.post):

            async def _await() -> T_RESP:
                response = await client.post(path, **kwargs)  # type: ignore
                return process_response(response)

            return _await()

        response = client.post(path, **kwargs)  # type: ignore
        return process_response(response)
