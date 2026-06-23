"""Base endpoint mix-in for all API resource endpoints."""

from __future__ import annotations

import warnings
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    TypeVar,
    Union,
    overload,
)

from imednet.constants import DEFAULT_PAGE_SIZE
from imednet.core.endpoint.abc import EndpointABC
from imednet.core.endpoint.operations import FilterGetOperation, ListOperation
from imednet.core.endpoint.strategies import (
    DefaultParamProcessor,
    KeepStudyKeyStrategy,
    OptionalStudyKeyStrategy,
    StudyKeyStrategy,
)
from imednet.core.endpoint.structs import ListRequestState, ParamState
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.parsing import get_model_parser
from imednet.core.protocols import AsyncRequestorProtocol, ParamProcessor, RequestorProtocol
from imednet.models.json_base import JsonModel
from imednet.utils.filters import build_filter_string
from imednet.utils.typing import FilterValue, ItemId
from imednet.utils.url import build_safe_path

T = TypeVar("T", bound=JsonModel)
ClientT = TypeVar("ClientT", bound=Union[RequestorProtocol, AsyncRequestorProtocol])
ClientT = TypeVar("ClientT", bound=Union[RequestorProtocol, AsyncRequestorProtocol])


class GenericEndpoint(EndpointABC[T], Generic[T, ClientT]):
    """Generic base for endpoint wrappers.

    Handles context injection and basic path building.
    Does NOT include EDC-specific logic.
    """

    BASE_PATH = ""
    _client: Optional[RequestorProtocol]
    _async_client: Optional[AsyncRequestorProtocol]

    def __init__(
        self,
        client: Optional[RequestorProtocol] = None,
        ctx: object | None = None,
        async_client: Optional[AsyncRequestorProtocol] = None,
    ) -> None:
        """TODO: Add docstring."""
        if ctx is not None:
            warnings.warn(
                "The 'ctx' constructor argument is deprecated and ignored. "
                "Pass study_key explicitly or use ImednetSDK.study_context(...).",
                DeprecationWarning,
                stacklevel=2,
            )
        self._client = client
        self._async_client = async_client

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Pass-through for filters in generic endpoints."""
        return filters

    def _build_path(self, *segments: Any) -> str:
        """Return an API path joined with :data:`BASE_PATH`.

        Args:
            *segments: URL path segments to append.

        Returns:
            The full API path string.
        """
        return "/" + build_safe_path(self.BASE_PATH, *segments)

    def _require_sync_client(self) -> RequestorProtocol:
        """Return the configured sync client or raise if missing."""
        if self._client is None:
            raise RuntimeError("Sync client not configured")
        return self._client

    def _require_async_client(self) -> AsyncRequestorProtocol:
        """Return the configured async client or raise if missing."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return self._async_client


class _ListGetEndpointBase(GenericEndpoint[T, ClientT]):
    """Generic base for endpoints that provide list and get-by-filter functionality.

    Uses composable operations to provide standard list/get read operations.
    """

    PAGE_SIZE: int = DEFAULT_PAGE_SIZE
    PAGINATOR_CLS: type[Paginator] = Paginator
    ASYNC_PAGINATOR_CLS: type[AsyncPaginator] = AsyncPaginator
    PARAM_PROCESSOR: Optional[ParamProcessor] = None
    PARAM_PROCESSOR_CLS: type[ParamProcessor] = DefaultParamProcessor
    STUDY_KEY_STRATEGY: Optional[StudyKeyStrategy] = None

    @property
    def study_key_strategy(self) -> StudyKeyStrategy:
        """TODO: Add docstring."""
        if self.STUDY_KEY_STRATEGY:
            return self.STUDY_KEY_STRATEGY
        if self.requires_study_key:
            return KeepStudyKeyStrategy()
        return OptionalStudyKeyStrategy()

    @property
    def param_processor(self) -> ParamProcessor:
        """TODO: Add docstring."""
        if self.PARAM_PROCESSOR:
            return self.PARAM_PROCESSOR
        return self.PARAM_PROCESSOR_CLS()

    def _parse_item(self, item: Any) -> T:
        """TODO: Add docstring."""
        parse_func = get_model_parser(self.MODEL)
        return parse_func(item)

    def _resolve_parse_func(self) -> Callable[[Any], T]:
        """TODO: Add docstring."""
        return self._parse_item

    def _resolve_params(
        self,
        study_key: Optional[str],
        extra_params: Optional[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> ParamState:
        """TODO: Add docstring."""
        filters = self._auto_filter(filters.copy())

        processed_filters, special_params = self.param_processor.process_filters(filters)
        if special_params:
            if extra_params is None:
                extra_params = {}
            else:
                extra_params = extra_params.copy()
            extra_params.update(special_params)

        if study_key:
            processed_filters["studyKey"] = study_key

        study, processed_filters = self.study_key_strategy.process(processed_filters)
        self._validate_study_key(study)

        other_filters = {k: v for k, v in processed_filters.items() if k != "studyKey"}

        params: Dict[str, Any] = {}
        if processed_filters:
            params["filter"] = build_filter_string(processed_filters)
        if extra_params:
            params.update(extra_params)

        return ParamState(study=study, params=params, other_filters=other_filters)

    def _prepare_list_request(
        self,
        study_key: Optional[str],
        extra_params: Optional[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> ListRequestState[T]:
        """TODO: Add docstring."""
        param_state = self._resolve_params(study_key, extra_params, filters)
        study = param_state.study
        params = param_state.params

        path = self._get_endpoint_path(study)
        return ListRequestState(
            path=path,
            params=params,
            study=study,
        )

    def _validate_get_result(self, items: List[T], study_key: Optional[str], item_id: ItemId) -> T:
        """TODO: Add docstring."""
        if not items:
            self._raise_not_found(study_key, item_id)
        return items[0]

    @staticmethod
    def _require_item_id(item_id: ItemId) -> None:
        """TODO: Add docstring."""
        if item_id is None:
            raise TypeError("Missing required argument: item_id")


class ListGetEndpoint(_ListGetEndpointBase[T, ClientT]):
    """Unified generic base for endpoints that provide list and get-by-filter functionality."""

    def __init__(
        self,
        client: ClientT,
        ctx: object | None = None,
    ) -> None:
        """TODO: Add docstring."""
        from imednet.core.protocols import AsyncRequestorProtocol

        is_async = False
        if isinstance(client, AsyncRequestorProtocol):
            is_async = True
        elif type(client).__name__ == "AsyncMock" or "Async" in type(client).__name__:
            is_async = True
        elif getattr(client, "get", None) and "Async" in type(client.get).__name__:
            is_async = True

        if is_async:
            super().__init__(async_client=client, ctx=ctx)
        else:
            super().__init__(client=client, ctx=ctx)

    def _list_sync(
        self,
        client: RequestorProtocol,
        paginator_cls: type[Paginator],
        *,
        study_key: Optional[str] = None,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> Iterator[T]:
        """TODO: Add docstring."""
        state = self._prepare_list_request(study_key, extra_params, filters)
        return ListOperation[T](
            path=state.path,
            params=state.params,
            page_size=self.PAGE_SIZE,
            parse_func=self._resolve_parse_func(),
        ).execute_sync(client, paginator_cls)

    def _list_async(
        self,
        client: AsyncRequestorProtocol,
        paginator_cls: type[AsyncPaginator],
        *,
        study_key: Optional[str] = None,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> AsyncIterator[T]:
        """TODO: Add docstring."""
        state = self._prepare_list_request(study_key, extra_params, filters)
        return ListOperation[T](
            path=state.path,
            params=state.params,
            page_size=self.PAGE_SIZE,
            parse_func=self._resolve_parse_func(),
        ).execute_async(client, paginator_cls)

    @overload
    def list(
        self: "ListGetEndpoint[T, RequestorProtocol]",
        study_key: Optional[str] = None,
        **filters: FilterValue,
    ) -> Iterator[T]: ...

    @overload
    def list(
        self: "ListGetEndpoint[T, AsyncRequestorProtocol]",
        study_key: Optional[str] = None,
        **filters: FilterValue,
    ) -> AsyncIterator[T]: ...

    def list(
        self, study_key: Optional[str] = None, **filters: FilterValue
    ) -> Union[Iterator[T], AsyncIterator[T]]:
        """TODO: Add docstring."""
        _filters: Dict[str, Any] = dict(filters)
        if self._async_client:
            return self._list_async(
                self._require_async_client(),
                self.ASYNC_PAGINATOR_CLS,
                study_key=study_key,
                **_filters,
            )
        else:
            return self._list_sync(
                self._require_sync_client(),
                self.PAGINATOR_CLS,
                study_key=study_key,
                **_filters,
            )

    def _get_sync(
        self,
        client: RequestorProtocol,
        paginator_cls: type[Paginator],
        *,
        study_key: Optional[str],
        item_id: ItemId,
    ) -> T:
        """TODO: Add docstring."""
        filters: Dict[str, Any] = {self._id_param: item_id}
        operation = FilterGetOperation[T](
            study_key=study_key,
            item_id=item_id,
            filters=filters,
            validate_func=self._validate_get_result,
            list_sync_func=lambda *a, **k: list(self._list_sync(*a, **k)),
        )
        return operation.execute_sync(client, paginator_cls)

    async def _get_async(
        self,
        client: AsyncRequestorProtocol,
        paginator_cls: type[AsyncPaginator],
        *,
        study_key: Optional[str],
        item_id: ItemId,
    ) -> T:
        """TODO: Add docstring."""
        filters: Dict[str, Any] = {self._id_param: item_id}

        async def _list_async_for_get(*a: Any, **k: Any) -> List[T]:
            res = []
            async for item in self._list_async(*a, **k):
                res.append(item)
            return res

        operation = FilterGetOperation[T](
            study_key=study_key,
            item_id=item_id,
            filters=filters,
            validate_func=self._validate_get_result,
            list_async_func=_list_async_for_get,
        )
        return await operation.execute_async(client, paginator_cls)

    @overload
    def get(
        self: "ListGetEndpoint[T, RequestorProtocol]", study_key: Optional[str], item_id: ItemId
    ) -> T: ...

    @overload
    def get(
        self: "ListGetEndpoint[T, AsyncRequestorProtocol]",
        study_key: Optional[str],
        item_id: ItemId,
    ) -> Awaitable[T]: ...

    def get(self, study_key: Optional[str], item_id: ItemId) -> Union[T, Awaitable[T]]:
        """TODO: Add docstring."""
        self._require_item_id(item_id)
        if self._async_client:
            return self._get_async(
                self._require_async_client(),
                self.ASYNC_PAGINATOR_CLS,
                study_key=study_key,
                item_id=item_id,
            )
        else:
            return self._get_sync(
                self._require_sync_client(),
                self.PAGINATOR_CLS,
                study_key=study_key,
                item_id=item_id,
            )

    # Backward compatible aliases
    def async_list(  # pragma: no cover
        self, study_key: Optional[str] = None, **filters: FilterValue
    ) -> AsyncIterator[T]:
        """Alias for list()."""
        import warnings

        warnings.warn("async_list is deprecated, use list()", DeprecationWarning, stacklevel=2)
        return self.list(study_key=study_key, **filters)  # type: ignore

    def async_get(self, study_key: Optional[str], item_id: ItemId) -> Awaitable[T]:
        """Alias for get()."""
        import warnings

        warnings.warn("async_get is deprecated, use get()", DeprecationWarning, stacklevel=2)
        return self.get(study_key=study_key, item_id=item_id)  # type: ignore

    # Backward compatible aliases
    def async_list(  # pragma: no cover
        self, study_key: Optional[str] = None, **filters: FilterValue
    ) -> AsyncIterator[T]:
        """Alias for list()."""
        import warnings

        warnings.warn("async_list is deprecated, use list()", DeprecationWarning, stacklevel=2)
        return self.list(study_key=study_key, **filters)  # type: ignore

    def async_get(self, study_key: Optional[str], item_id: ItemId) -> Awaitable[T]:
        """Alias for get()."""
        import warnings

        warnings.warn("async_get is deprecated, use get()", DeprecationWarning, stacklevel=2)
        return self.get(study_key=study_key, item_id=item_id)  # type: ignore


# Backward-compatible aliases
SyncListGetEndpoint = ListGetEndpoint
AsyncListGetEndpoint = ListGetEndpoint
GenericListGetEndpoint = ListGetEndpoint


class ListGetEndpoint(_ListGetEndpointBase[T, ClientT]):
    """Unified generic base for endpoints that provide list and get-by-filter functionality."""

    def __init__(
        self,
        client: ClientT,
        ctx: object | None = None,
    ) -> None:
        """TODO: Add docstring."""
        if (
            hasattr(client, "aclose") or "Async" in type(client).__name__
        ):  # Best-effort async check if not isinstance
            # More strictly, try to check protocol
            pass
        if getattr(client, "is_async", False) or getattr(client, "_is_async", False):
            pass  # We'll just rely on isinstance. But RequestorProtocol is a Protocol.
        # Actually it's safer to check for async-specific methods like `request_async`
        # But we can just assign appropriately:
        is_async = (
            hasattr(client, "request")
            and getattr(client.request, "__code__", None)
            and getattr(client.request.__code__, "co_flags", 0) & 0x80
        )
        # Simpler: check if `request` is a coroutine function, but it's a protocol.
        # The easiest way is to check `isinstance(client, AsyncRequestorProtocol)` if it's a runtime checkable protocol.

        # Let's just assign based on what type of methods exist, or both if needed, but the original GenericEndpoint takes them as explicit kwargs.
        from imednet.core.protocols import AsyncRequestorProtocol

        if isinstance(client, AsyncRequestorProtocol):
            super().__init__(async_client=client, ctx=ctx)
        else:
            super().__init__(client=client, ctx=ctx)

    def _list_sync(
        self,
        client: RequestorProtocol,
        paginator_cls: type[Paginator],
        *,
        study_key: Optional[str] = None,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> Iterator[T]:
        """TODO: Add docstring."""
        state = self._prepare_list_request(study_key, extra_params, filters)
        return ListOperation[T](
            path=state.path,
            params=state.params,
            page_size=self.PAGE_SIZE,
            parse_func=self._resolve_parse_func(),
        ).execute_sync(client, paginator_cls)

    def _list_async(
        self,
        client: AsyncRequestorProtocol,
        paginator_cls: type[AsyncPaginator],
        *,
        study_key: Optional[str] = None,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> AsyncIterator[T]:
        """TODO: Add docstring."""
        state = self._prepare_list_request(study_key, extra_params, filters)
        return ListOperation[T](
            path=state.path,
            params=state.params,
            page_size=self.PAGE_SIZE,
            parse_func=self._resolve_parse_func(),
        ).execute_async(client, paginator_cls)

    @overload
    def list(
        self: "ListGetEndpoint[T, RequestorProtocol]",
        study_key: Optional[str] = None,
        **filters: FilterValue,
    ) -> Iterator[T]: ...

    @overload
    def list(
        self: "ListGetEndpoint[T, AsyncRequestorProtocol]",
        study_key: Optional[str] = None,
        **filters: FilterValue,
    ) -> AsyncIterator[T]: ...

    def list(
        self, study_key: Optional[str] = None, **filters: FilterValue
    ) -> Union[Iterator[T], AsyncIterator[T]]:
        """TODO: Add docstring."""
        _filters: Dict[str, Any] = dict(filters)
        if self._async_client:
            return self._list_async(
                self._require_async_client(),
                self.ASYNC_PAGINATOR_CLS,
                study_key=study_key,
                **_filters,
            )
        else:
            return self._list_sync(
                self._require_sync_client(),
                self.PAGINATOR_CLS,
                study_key=study_key,
                **_filters,
            )

    def _get_sync(
        self,
        client: RequestorProtocol,
        paginator_cls: type[Paginator],
        *,
        study_key: Optional[str],
        item_id: ItemId,
    ) -> T:
        """TODO: Add docstring."""
        filters: Dict[str, Any] = {self._id_param: item_id}
        operation = FilterGetOperation[T](
            study_key=study_key,
            item_id=item_id,
            filters=filters,
            validate_func=self._validate_get_result,
            list_sync_func=lambda *a, **k: list(self._list_sync(*a, **k)),
        )
        return operation.execute_sync(client, paginator_cls)

    async def _get_async(
        self,
        client: AsyncRequestorProtocol,
        paginator_cls: type[AsyncPaginator],
        *,
        study_key: Optional[str],
        item_id: ItemId,
    ) -> T:
        """TODO: Add docstring."""
        filters: Dict[str, Any] = {self._id_param: item_id}

        async def _list_async_for_get(*a: Any, **k: Any) -> List[T]:
            res = []
            async for item in self._list_async(*a, **k):
                res.append(item)
            return res

        operation = FilterGetOperation[T](
            study_key=study_key,
            item_id=item_id,
            filters=filters,
            validate_func=self._validate_get_result,
            list_async_func=_list_async_for_get,
        )
        return await operation.execute_async(client, paginator_cls)

    @overload
    def get(
        self: "ListGetEndpoint[T, RequestorProtocol]", study_key: Optional[str], item_id: ItemId
    ) -> T: ...

    @overload
    def get(
        self: "ListGetEndpoint[T, AsyncRequestorProtocol]",
        study_key: Optional[str],
        item_id: ItemId,
    ) -> Awaitable[T]: ...

    def get(self, study_key: Optional[str], item_id: ItemId) -> Union[T, Awaitable[T]]:
        """TODO: Add docstring."""
        self._require_item_id(item_id)
        if self._async_client:
            return self._get_async(
                self._require_async_client(),
                self.ASYNC_PAGINATOR_CLS,
                study_key=study_key,
                item_id=item_id,
            )
        else:
            return self._get_sync(
                self._require_sync_client(),
                self.PAGINATOR_CLS,
                study_key=study_key,
                item_id=item_id,
            )

    # Backward compatible aliases
    def async_list(  # pragma: no cover
        self, study_key: Optional[str] = None, **filters: FilterValue
    ) -> AsyncIterator[T]:
        """Alias for list()."""
        import warnings

        warnings.warn("async_list is deprecated, use list()", DeprecationWarning, stacklevel=2)
        return self.list(study_key=study_key, **filters)  # type: ignore

    def async_get(self, study_key: Optional[str], item_id: ItemId) -> Awaitable[T]:
        """Alias for get()."""
        import warnings

        warnings.warn("async_get is deprecated, use get()", DeprecationWarning, stacklevel=2)
        return self.get(study_key=study_key, item_id=item_id)  # type: ignore


# Backward-compatible aliases
SyncListGetEndpoint = ListGetEndpoint
AsyncListGetEndpoint = ListGetEndpoint
GenericListGetEndpoint = ListGetEndpoint
