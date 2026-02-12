from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Dict, Generic, Iterable, List, Optional, Type, cast

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.models.json_base import JsonModel

from .parsing import ParsingMixin, T


class FilterGetEndpointMixin(Generic[T], ABC):
    """Mixin implementing ``get`` via filtering."""

    requires_study_key: bool = True

    @property
    @abstractmethod
    def MODEL(self) -> Type[T]:
        """The model class associated with this endpoint."""
        ...

    @property
    @abstractmethod
    def _id_param(self) -> str:
        """The parameter name for the ID filter."""
        ...

    @abstractmethod
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
        ...

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


class PathGetEndpointMixin(ParsingMixin[T], ABC):
    """Mixin implementing ``get`` via direct path."""

    requires_study_key: bool = True

    @property
    @abstractmethod
    def PATH(self) -> str:
        """The relative path for this endpoint."""
        ...

    @abstractmethod
    def _build_path(self, *segments: Any) -> str:
        """Build the API path."""
        ...

    def _get_path_for_id(self, study_key: Optional[str], item_id: Any) -> str:
        segments: Iterable[Any]
        if self.requires_study_key:
            if not study_key:
                raise ValueError("Study key must be provided")
            segments = (study_key, self.PATH, item_id)
        else:
            segments = (self.PATH, item_id) if self.PATH else (item_id,)

        # No cast needed
        return self._build_path(*segments)

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
            # We assume response has json() method (httpx.Response)
            # Since client returns Response object, we rely on duck typing or we can cast
            # RequestorProtocol returns Any, but usually httpx.Response
            data = response.json()
            if not data:
                # Enforce strict validation for empty body
                self._raise_not_found(study_key, item_id)
            return self._parse_item(data)

        if is_async:

            async def _await() -> T:
                # client is expected to be AsyncRequestorProtocol
                aclient = cast(AsyncRequestorProtocol, client)
                response = await aclient.get(path)
                return process_response(response)

            return _await()

        sclient = cast(RequestorProtocol, client)
        response = sclient.get(path)
        return process_response(response)
