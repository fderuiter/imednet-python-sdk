"""Base endpoint mix-in for all API resource endpoints."""

from __future__ import annotations

import warnings
from typing import Any, AsyncIterator, Callable, Dict, Iterator, List, Optional, TypeVar

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
from imednet.core.protocols import AsyncRequesterProtocol, ParamProcessor, RequesterProtocol
from imednet.models.base import ImednetBaseModel
from imednet.utils.filters import build_filter_string
from imednet.utils.typing import FilterValue, ItemId
from imednet.utils.url import build_safe_path

T = TypeVar("T", bound=ImednetBaseModel)


class GenericEndpoint(EndpointABC[T]):
    """Generic base for endpoint wrappers.

    Handles context injection and basic path building.
    Does NOT include EDC-specific logic.
    """

    BASE_PATH = ""
    _client: Optional[RequesterProtocol]
    _async_client: Optional[AsyncRequesterProtocol]

    def __init__(
        self,
        client: Optional[RequesterProtocol] = None,
        ctx: object | None = None,
        async_client: Optional[AsyncRequesterProtocol] = None,
    ) -> None:
        """Initialize the generic endpoint.

        Args:
            client: Synchronous requester instance.
            ctx: Deprecated context object.
            async_client: Asynchronous requester instance.
        """
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

    def _require_sync_client(self) -> RequesterProtocol:
        """Return the configured sync client or raise if missing."""
        if self._client is None:
            raise RuntimeError("Sync client not configured")
        return self._client

    def _require_async_client(self) -> AsyncRequesterProtocol:
        """Return the configured async client or raise if missing."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return self._async_client


class _ListGetEndpointBase(GenericEndpoint[T]):
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
        """Return the strategy for handling study keys in this endpoint."""
        if self.STUDY_KEY_STRATEGY:
            return self.STUDY_KEY_STRATEGY
        if self.requires_study_key:
            return KeepStudyKeyStrategy()
        return OptionalStudyKeyStrategy()

    @property
    def param_processor(self) -> ParamProcessor:
        """Return the parameter processor for this endpoint."""
        if self.PARAM_PROCESSOR:
            return self.PARAM_PROCESSOR
        return self.PARAM_PROCESSOR_CLS()

    def _parse_item(self, item: Any) -> T:
        """Parse a raw API item into a Pydantic model instance."""
        parse_func = get_model_parser(self.MODEL)
        return parse_func(item)

    def _resolve_parse_func(self) -> Callable[[Any], T]:
        """Return the function used to parse items for this endpoint."""
        return self._parse_item

    def _resolve_params(
        self,
        study_key: Optional[str],
        extra_params: Optional[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> ParamState:
        """Resolve filters and extra parameters into a ParamState.

        Args:
            study_key: The study key to use.
            extra_params: Additional query parameters.
            filters: Key-value filters to apply.

        Returns:
            A ParamState containing the resolved study, parameters, and other filters.
        """
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
        """Prepare the state required for a list request.

        Args:
            study_key: Optional study key override.
            extra_params: Additional query parameters.
            filters: Resource filters.

        Returns:
            A ListRequestState containing path and resolved parameters.
        """
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
        """Validate that a get operation returned exactly one item.

        Args:
            items: The list of items returned by the filter.
            study_key: The study key used for the request.
            item_id: The ID of the item being requested.

        Returns:
            The first item in the list.

        Raises:
            NotFoundError: If the list is empty.
        """
        if not items:
            self._raise_not_found(study_key, item_id)
        return items[0]

    @staticmethod
    def _require_item_id(item_id: ItemId) -> None:
        """Ensure that an item ID was provided."""
        if item_id is None:
            raise TypeError("Missing required argument: item_id")


class SyncListGetEndpoint(_ListGetEndpointBase[T]):
    """Synchronous endpoint providing list and get functionality."""

    def __init__(
        self,
        client: RequesterProtocol,
        ctx: object | None = None,
    ) -> None:
        """Initialize the synchronous endpoint.

        Args:
            client: Synchronous requester instance.
            ctx: Deprecated context object.
        """
        super().__init__(client=client, ctx=ctx)

    def _list_sync(
        self,
        client: RequesterProtocol,
        paginator_cls: type[Paginator],
        *,
        study_key: Optional[str] = None,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> Iterator[T]:
        """Internal synchronous list implementation.

        Args:
            client: Requester to use.
            paginator_cls: Paginator class to use.
            study_key: Optional study key.
            extra_params: Additional query parameters.
            **filters: Resource filters.

        Returns:
            An iterator over the items.
        """
        state = self._prepare_list_request(study_key, extra_params, filters)
        return ListOperation[T](
            path=state.path,
            params=state.params,
            page_size=self.PAGE_SIZE,
            parse_func=self._resolve_parse_func(),
        ).execute_sync(client, paginator_cls)

    def list(self, study_key: Optional[str] = None, **filters: FilterValue) -> Iterator[T]:
        """List resources matching the given filters.

        Args:
            study_key: Optional study key to override the default.
            **filters: Resource filters.

        Returns:
            An iterator over the matching resources.
        """
        # Cast FilterValue → Any at the public/internal boundary to satisfy
        # mypy's invariant dict type-checking on `_list_sync`'s **filters: Any.
        _filters: Dict[str, Any] = dict(filters)
        return self._list_sync(
            self._require_sync_client(),
            self.PAGINATOR_CLS,
            study_key=study_key,
            **_filters,
        )

    def _get_sync(
        self,
        client: RequesterProtocol,
        paginator_cls: type[Paginator],
        *,
        study_key: Optional[str],
        item_id: ItemId,
    ) -> T:
        """Internal synchronous get implementation.

        Args:
            client: Requester to use.
            paginator_cls: Paginator class to use.
            study_key: Optional study key.
            item_id: The ID of the item to retrieve.

        Returns:
            The requested item.
        """
        filters: Dict[str, Any] = {self._id_param: item_id}
        operation = FilterGetOperation[T](
            study_key=study_key,
            item_id=item_id,
            filters=filters,
            validate_func=self._validate_get_result,
            list_sync_func=lambda *a, **k: list(self._list_sync(*a, **k)),
        )
        return operation.execute_sync(client, paginator_cls)

    def get(self, study_key: Optional[str], item_id: ItemId) -> T:
        """Retrieve a single resource by its ID.

        Args:
            study_key: The study key.
            item_id: The ID of the resource to retrieve.

        Returns:
            The requested resource.
        """
        self._require_item_id(item_id)
        return self._get_sync(
            self._require_sync_client(),
            self.PAGINATOR_CLS,
            study_key=study_key,
            item_id=item_id,
        )


class AsyncListGetEndpoint(_ListGetEndpointBase[T]):
    """Asynchronous endpoint providing list and get functionality."""

    def __init__(
        self,
        async_client: AsyncRequesterProtocol,
        ctx: object | None = None,
    ) -> None:
        """Initialize the asynchronous endpoint.

        Args:
            async_client: Asynchronous requester instance.
            ctx: Deprecated context object.
        """
        super().__init__(ctx=ctx, async_client=async_client)

    def _list_async(
        self,
        client: AsyncRequesterProtocol,
        paginator_cls: type[AsyncPaginator],
        *,
        study_key: Optional[str] = None,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> AsyncIterator[T]:
        """Internal asynchronous list implementation.

        Args:
            client: Asynchronous requester to use.
            paginator_cls: Asynchronous paginator class to use.
            study_key: Optional study key.
            extra_params: Additional query parameters.
            **filters: Resource filters.

        Returns:
            An asynchronous iterator over the items.
        """
        state = self._prepare_list_request(study_key, extra_params, filters)
        return ListOperation[T](
            path=state.path,
            params=state.params,
            page_size=self.PAGE_SIZE,
            parse_func=self._resolve_parse_func(),
        ).execute_async(client, paginator_cls)

    def async_list(
        self, study_key: Optional[str] = None, **filters: FilterValue
    ) -> AsyncIterator[T]:
        """List resources matching the given filters asynchronously.

        Args:
            study_key: Optional study key override.
            **filters: Resource filters.

        Returns:
            An asynchronous iterator over the matching resources.
        """
        # Cast FilterValue → Any at the public/internal boundary.
        _filters: Dict[str, Any] = dict(filters)
        return self._list_async(
            self._require_async_client(),
            self.ASYNC_PAGINATOR_CLS,
            study_key=study_key,
            **_filters,
        )

    async def _get_async(
        self,
        client: AsyncRequesterProtocol,
        paginator_cls: type[AsyncPaginator],
        *,
        study_key: Optional[str],
        item_id: ItemId,
    ) -> T:
        """Internal asynchronous get implementation.

        Args:
            client: Asynchronous requester to use.
            paginator_cls: Asynchronous paginator class to use.
            study_key: Optional study key.
            item_id: The ID of the item to retrieve.

        Returns:
            The requested item.
        """
        filters: Dict[str, Any] = {self._id_param: item_id}
        operation = FilterGetOperation[T](
            study_key=study_key,
            item_id=item_id,
            filters=filters,
            validate_func=self._validate_get_result,
            list_async_func=self._list_async_for_get,
        )
        return await operation.execute_async(client, paginator_cls)

    async def _list_async_for_get(self, *a: Any, **k: Any) -> List[T]:
        """Helper to collect async list results into a list for get validation."""
        res = []
        async for item in self._list_async(*a, **k):
            res.append(item)
        return res

    async def async_get(self, study_key: Optional[str], item_id: ItemId) -> T:
        """Retrieve a single resource by its ID asynchronously.

        Args:
            study_key: The study key.
            item_id: The ID of the resource to retrieve.

        Returns:
            The requested resource.
        """
        self._require_item_id(item_id)
        return await self._get_async(
            self._require_async_client(),
            self.ASYNC_PAGINATOR_CLS,
            study_key=study_key,
            item_id=item_id,
        )


# Backward-compatible alias. New code should use SyncListGetEndpoint / AsyncListGetEndpoint.
GenericListGetEndpoint = SyncListGetEndpoint
