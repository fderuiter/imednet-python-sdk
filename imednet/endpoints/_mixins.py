from __future__ import annotations

import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.json_base import JsonModel
from imednet.utils.filters import build_filter_string

if TYPE_CHECKING:  # pragma: no cover - imported for type hints only

    class _EndpointBase(Protocol):
        def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]: ...
        def _build_path(self, *segments: Any) -> str: ...

        PATH: str
        MODEL: Type[JsonModel]
        _id_param: str
        _cache_name: Optional[str]
        requires_study_key: bool
        PAGE_SIZE: int


T = TypeVar("T", bound=JsonModel)


class ListGetEndpointMixin(Generic[T]):
    """Mixin implementing ``list`` and ``get`` helpers."""

    PATH: str
    MODEL: Type[T]
    _id_param: str
    _cache_name: Optional[str] = None
    requires_study_key: bool = True
    PAGE_SIZE: int = 100
    _pop_study_filter: bool = False
    _missing_study_exception: type[Exception] = ValueError

    def _parse_item(self, item: Any) -> T:
        if hasattr(self.MODEL, "from_json"):
            return getattr(self.MODEL, "from_json")(item)
        return self.MODEL.model_validate(item)

    def _update_local_cache(
        self,
        result: list[T],
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

    def _process_filters(self, filters: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Process filters and extract extra parameters.

        Args:
            filters: The filters dictionary.

        Returns:
            Tuple containing (cleaned_filters, extra_params)
        """
        return filters, {}

    def _prepare_list_params(
        self,
        study_key: Optional[str],
        refresh: bool,
        extra_params: Optional[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> Tuple[Optional[List[T]], str, Dict[str, Any], Optional[str], Any, bool]:
        """
        Prepare parameters for list request.

        Returns:
            Tuple of (cached_result, path, params, study, cache_obj, has_other_filters)
        """
        filters, processed_extra = self._process_filters(filters)
        if extra_params:
            processed_extra.update(extra_params)

        filters = self._auto_filter(filters)
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

        cache = getattr(self, self._cache_name, None) if self._cache_name else None
        other_filters = {k: v for k, v in filters.items() if k != "studyKey"}
        has_other_filters = bool(other_filters)

        if self.requires_study_key:
            if not study:
                raise ValueError("Study key must be provided or set in the context")
            if cache is not None and not has_other_filters and not refresh and study in cache:
                return cache[study], "", {}, study, cache, False
        else:
            if cache is not None and not has_other_filters and not refresh and cache is not None:
                return cache, "", {}, study, cache, False

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)
        if processed_extra:
            params.update(processed_extra)

        segments: Iterable[Any]
        if self.requires_study_key:
            segments = (study, self.PATH)
        else:
            segments = (self.PATH,) if self.PATH else ()

        path = self._build_path(*segments)
        return None, path, params, study, cache, has_other_filters

    def _get_parse_func(self) -> Any:
        if self._parse_item.__func__ is not ListGetEndpointMixin._parse_item:
            return self._parse_item

        parse_func = getattr(self.MODEL, "from_json", None)
        if parse_func is None:
            parse_func = self.MODEL.model_validate
        return parse_func

    def _list_sync(
        self,
        client: Client,
        *,
        study_key: Optional[str] = None,
        refresh: bool = False,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> List[T]:
        cached, path, params, study, cache_obj, has_other_filters = self._prepare_list_params(
            study_key, refresh, extra_params, filters
        )
        if cached is not None:
            return cached

        paginator = Paginator(client, path, params=params, page_size=self.PAGE_SIZE)
        parse_func = self._get_parse_func()

        result = [parse_func(item) for item in paginator]

        self._update_local_cache(result, study, has_other_filters, cache_obj)
        return result

    async def _list_async(
        self,
        client: AsyncClient,
        *,
        study_key: Optional[str] = None,
        refresh: bool = False,
        extra_params: Optional[Dict[str, Any]] = None,
        **filters: Any,
    ) -> List[T]:
        cached, path, params, study, cache_obj, has_other_filters = self._prepare_list_params(
            study_key, refresh, extra_params, filters
        )
        if cached is not None:
            return cached

        paginator = AsyncPaginator(client, path, params=params, page_size=self.PAGE_SIZE)
        parse_func = self._get_parse_func()

        result = [parse_func(item) async for item in paginator]

        self._update_local_cache(result, study, has_other_filters, cache_obj)
        return result

    def _get_sync(
        self,
        client: Client,
        *,
        study_key: Optional[str],
        item_id: Any,
    ) -> T:
        filters = {self._id_param: item_id}
        results = self._list_sync(
            client,
            study_key=study_key,
            refresh=True,
            **filters,
        )
        if not results:
            if self.requires_study_key:
                raise ValueError(f"{self.MODEL.__name__} {item_id} not found in study {study_key}")
            raise ValueError(f"{self.MODEL.__name__} {item_id} not found")
        return results[0]

    async def _get_async(
        self,
        client: AsyncClient,
        *,
        study_key: Optional[str],
        item_id: Any,
    ) -> T:
        filters = {self._id_param: item_id}
        results = await self._list_async(
            client,
            study_key=study_key,
            refresh=True,
            **filters,
        )
        if not results:
            if self.requires_study_key:
                raise ValueError(f"{self.MODEL.__name__} {item_id} not found in study {study_key}")
            raise ValueError(f"{self.MODEL.__name__} {item_id} not found")
        return results[0]


class ListGetEndpoint(BaseEndpoint, ListGetEndpointMixin[T]):
    """Endpoint base class implementing ``list`` and ``get`` helpers."""

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        return self._list_sync(
            self._client,
            study_key=study_key,
            **filters
        )

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        return await self._list_async(
            self._require_async_client(),
            study_key=study_key,
            **filters
        )

    def get(self, study_key: Optional[str], item_id: Any) -> T:
        return self._get_sync(
            self._client,
            study_key=study_key,
            item_id=item_id
        )

    async def async_get(self, study_key: Optional[str], item_id: Any) -> T:
        return await self._get_async(
            self._require_async_client(),
            study_key=study_key,
            item_id=item_id
        )
