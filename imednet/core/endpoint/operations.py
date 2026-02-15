"""Mixins for endpoint operations."""

from __future__ import annotations

from typing import Any, Awaitable, Generic, List, Optional, TypeVar, cast

from imednet.models.json_base import JsonModel

T = TypeVar("T", bound=JsonModel)


class GetOperationMixin(Generic[T]):
    """Mixin for GET operations."""

    def _execute_get(
        self,
        is_async: bool,
        study_key: Optional[str],
        item_id: Any,
    ) -> T | Awaitable[T]:
        """Execute the GET operation."""
        raise NotImplementedError

    def get(self, study_key: Optional[str], item_id: Any) -> T:
        """Get an item by ID."""
        return cast(T, self._execute_get(False, study_key, item_id))

    async def async_get(self, study_key: Optional[str], item_id: Any) -> T:
        """Asynchronously get an item by ID."""
        return await cast(Awaitable[T], self._execute_get(True, study_key, item_id))


class ListOperationMixin(Generic[T]):
    """Mixin for LIST operations."""

    def _execute_list(
        self,
        is_async: bool,
        study_key: Optional[str],
        **filters: Any,
    ) -> List[T] | Awaitable[List[T]]:
        """Execute the LIST operation."""
        raise NotImplementedError

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        """List items."""
        return cast(List[T], self._execute_list(False, study_key, **filters))

    async def async_list(
        self,
        study_key: Optional[str] = None,
        **filters: Any,
    ) -> List[T]:
        """Asynchronously list items."""
        return await cast(
            Awaitable[List[T]],
            self._execute_list(True, study_key, **filters),
        )
