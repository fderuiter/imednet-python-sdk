from __future__ import annotations

import inspect
from typing import Any, Awaitable, Dict, Iterable, List, Optional, cast

from imednet.core.endpoint.abc import EndpointABC
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol

from .parsing import ParsingMixin, T


class FilterGetEndpointMixin(EndpointABC[T]):
    """Mixin implementing ``get`` via filtering."""

    # MODEL and _id_param are inherited from EndpointABC as abstract or properties

    # This should be provided by ListEndpointMixin or similar implementation
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

    def _validate_get_result(self, items: List[T], study_key: Optional[str], item_id: Any) -> T:
        if not items:
            if self.requires_study_key:
                raise ValueError(
                    f"{self.MODEL.__name__} {item_id} not found in study {study_key}"
                )
            raise ValueError(f"{self.MODEL.__name__} {item_id} not found")
        return items[0]

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
                return self._validate_get_result(items, study_key, item_id)

            return _await()

        # Sync path
        return self._validate_get_result(cast(List[T], result), study_key, item_id)


class PathGetEndpointMixin(ParsingMixin[T], EndpointABC[T]):
    """Mixin implementing ``get`` via direct path."""

    # PATH is inherited from EndpointABC as abstract

    def _get_path_for_id(self, study_key: Optional[str], item_id: Any) -> str:
        segments: Iterable[Any]
        if self.requires_study_key:
            if not study_key:
                raise ValueError("Study key must be provided")
            segments = (study_key, self.PATH, item_id)
        else:
            segments = (self.PATH, item_id) if self.PATH else (item_id,)

        # No cast needed as we inherit EndpointABC which defines _build_path
        return self._build_path(*segments)

    def _raise_not_found(self, study_key: Optional[str], item_id: Any) -> None:
        raise ValueError(f"{self.MODEL.__name__} not found")

    def _process_response(self, response: Any, study_key: Optional[str], item_id: Any) -> T:
        data = response.json()
        if not data:
            # Enforce strict validation for empty body
            self._raise_not_found(study_key, item_id)
        return self._parse_item(data)

    def _get_impl_path(
        self,
        client: RequestorProtocol | AsyncRequestorProtocol,
        *,
        study_key: Optional[str],
        item_id: Any,
        is_async: bool = False,
    ) -> T | Awaitable[T]:
        path = self._get_path_for_id(study_key, item_id)

        if is_async:

            async def _await() -> T:
                # We assume client is AsyncRequestorProtocol because is_async=True
                aclient = cast(AsyncRequestorProtocol, client)
                response = await aclient.get(path)
                return self._process_response(response, study_key, item_id)

            return _await()

        sclient = cast(RequestorProtocol, client)
        response = sclient.get(path)
        return self._process_response(response, study_key, item_id)
