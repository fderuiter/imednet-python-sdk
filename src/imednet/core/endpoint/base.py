"""
Base endpoint mix-in for all API resource endpoints.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, TypeVar
from urllib.parse import quote

from imednet.constants import DEFAULT_PAGE_SIZE
from imednet.core.context import Context
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

T = TypeVar("T", bound=JsonModel)


class GenericEndpoint(EndpointABC[T]):
    """
    Generic base for endpoint wrappers.

    Handles context injection and basic path building.
    Does NOT include EDC-specific logic.
    """

    BASE_PATH = ""
    _client: RequestorProtocol
    _async_client: Optional[AsyncRequestorProtocol]

    def __init__(
        self,
        client: RequestorProtocol,
        ctx: Context,
        async_client: Optional[AsyncRequestorProtocol] = None,
    ) -> None:
        self._client = client
        self._async_client = async_client
        self._ctx = ctx

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Pass-through for filters in generic endpoints."""
        return filters

    def _build_path(self, *segments: Any) -> str:
        """
        Return an API path joined with :data:`BASE_PATH`.

        Args:
            *segments: URL path segments to append.

        Returns:
            The full API path string.
        """
        base = self.BASE_PATH.strip("/")
        parts = [base] if base else []
        for seg in segments:
            text = str(seg).strip("/")
            if text:
                # Encode path segments to prevent traversal and injection
                parts.append(quote(text, safe=""))
        return "/" + "/".join(parts)

    def _require_sync_client(self) -> RequestorProtocol:
        """Return the configured sync client."""
        return self._client

    def _require_async_client(self) -> AsyncRequestorProtocol:
        """Return the configured async client or raise if missing."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return self._async_client


class GenericListGetEndpoint(
    GenericEndpoint[T],
):
    """
    Generic base for endpoints that provide list and get-by-filter functionality.

    Uses composable operations to provide standard list/get read operations.
    """

    PAGE_SIZE: int = DEFAULT_PAGE_SIZE
    PAGINATOR_CLS: type[Paginator] = Paginator
    ASYNC_PAGINATOR_CLS: type[AsyncPaginator] = AsyncPaginator
    PARAM_PROCESSOR: Optional[ParamProcessor] = None
    PARAM_PROCESSOR_CLS: type[ParamProcessor] = DefaultParamProcessor
    STUDY_KEY_STRATEGY: Optional[StudyKeyStrategy] = None

    def __init__(
        self,
        client: RequestorProtocol,
        ctx: Context,
        async_client: Optional[AsyncRequestorProtocol] = None,
    ) -> None:
        super().__init__(client, ctx, async_client)

    @property
    def study_key_strategy(self) -> StudyKeyStrategy:
        if self.STUDY_KEY_STRATEGY:
            return self.STUDY_KEY_STRATEGY
        if self.requires_study_key:
            return KeepStudyKeyStrategy()
        return OptionalStudyKeyStrategy()

    @property
    def param_processor(self) -> ParamProcessor:
        if self.PARAM_PROCESSOR:
            return self.PARAM_PROCESSOR
        return self.PARAM_PROCESSOR_CLS()

    def _parse_item(self, item: Any) -> T:
        parse_func = get_model_parser(self.MODEL)
        return parse_func(item)

    def _resolve_parse_func(self) -> Callable[[Any], T]:
        return self._parse_item

    def _resolve_params(
        self,
        study_key: Optional[str],
        extra_params: Optional[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> ParamState:
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
        param_state = self._resolve_params(study_key, extra_params, filters)
        study = param_state.study
        params = param_state.params
        other_filters = param_state.other_filters

        path = self._get_endpoint_path(study)
        return ListRequestState(
            path=path,
            params=params,
            study=study,
            has_filters=bool(other_filters),
        )

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
        state = self._prepare_list_request(study_key, extra_params, filters)

        return ListOperation[T](
            path=state.path,
            params=state.params,
            page_size=self.PAGE_SIZE,
            parse_func=self._resolve_parse_func(),
        ).execute_sync(client, paginator_cls)

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
        state = self._prepare_list_request(study_key, extra_params, filters)

        return await ListOperation[T](
            path=state.path,
            params=state.params,
            page_size=self.PAGE_SIZE,
            parse_func=self._resolve_parse_func(),
        ).execute_async(client, paginator_cls)

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        return self._list_sync(
            self._require_sync_client(),
            self.PAGINATOR_CLS,
            study_key=study_key,
            **filters,
        )

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        return await self._list_async(
            self._require_async_client(),
            self.ASYNC_PAGINATOR_CLS,
            study_key=study_key,
            **filters,
        )

    def _validate_get_result(self, items: List[T], study_key: Optional[str], item_id: Any) -> T:
        if not items:
            self._raise_not_found(study_key, item_id)
        return items[0]

    def _get_sync(
        self,
        client: RequestorProtocol,
        paginator_cls: type[Paginator],
        *,
        study_key: Optional[str],
        item_id: Any,
    ) -> T:
        filters = {self._id_param: item_id}
        operation = FilterGetOperation[T](
            study_key=study_key,
            item_id=item_id,
            filters=filters,
            validate_func=self._validate_get_result,
            list_sync_func=self._list_sync,
            list_async_func=self._list_async,
        )
        return operation.execute_sync(client, paginator_cls)

    async def _get_async(
        self,
        client: AsyncRequestorProtocol,
        paginator_cls: type[AsyncPaginator],
        *,
        study_key: Optional[str],
        item_id: Any,
    ) -> T:
        filters = {self._id_param: item_id}
        operation = FilterGetOperation[T](
            study_key=study_key,
            item_id=item_id,
            filters=filters,
            validate_func=self._validate_get_result,
            list_sync_func=self._list_sync,
            list_async_func=self._list_async,
        )
        return await operation.execute_async(client, paginator_cls)

    def get(self, study_key: Optional[str], item_id: Any) -> T:
        return self._get_sync(
            self._require_sync_client(),
            self.PAGINATOR_CLS,
            study_key=study_key,
            item_id=item_id,
        )

    async def async_get(self, study_key: Optional[str], item_id: Any) -> T:
        return await self._get_async(
            self._require_async_client(),
            self.ASYNC_PAGINATOR_CLS,
            study_key=study_key,
            item_id=item_id,
        )
