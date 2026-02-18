from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from imednet.core.endpoint.abc import EndpointABC
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol

from .parsing import ParsingMixin, T


class FilterGetEndpointMixin(EndpointABC[T]):
    """Mixin implementing ``get`` via filtering."""

    # MODEL and _id_param are inherited from EndpointABC as abstract or properties

    # These should be provided by ListEndpointMixin or similar implementation
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
        raise NotImplementedError

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
        raise NotImplementedError

    def _validate_get_result(self, items: List[T], study_key: Optional[str], item_id: Any) -> T:
        if not items:
            if self.requires_study_key:
                raise ValueError(f"{self.MODEL.__name__} {item_id} not found in study {study_key}")
            raise ValueError(f"{self.MODEL.__name__} {item_id} not found")
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
        result = self._list_sync(
            client,
            paginator_cls,
            study_key=study_key,
            refresh=True,
            **filters,
        )
        return self._validate_get_result(result, study_key, item_id)

    async def _get_async(
        self,
        client: AsyncRequestorProtocol,
        paginator_cls: type[AsyncPaginator],
        *,
        study_key: Optional[str],
        item_id: Any,
    ) -> T:
        filters = {self._id_param: item_id}
        result = await self._list_async(
            client,
            paginator_cls,
            study_key=study_key,
            refresh=True,
            **filters,
        )
        return self._validate_get_result(result, study_key, item_id)


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

    def _get_path_sync(
        self,
        client: RequestorProtocol,
        *,
        study_key: Optional[str],
        item_id: Any,
    ) -> T:
        path = self._get_path_for_id(study_key, item_id)
        response = client.get(path)
        return self._process_response(response, study_key, item_id)

    async def _get_path_async(
        self,
        client: AsyncRequestorProtocol,
        *,
        study_key: Optional[str],
        item_id: Any,
    ) -> T:
        path = self._get_path_for_id(study_key, item_id)
        response = await client.get(path)
        return self._process_response(response, study_key, item_id)
