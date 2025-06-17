"""Endpoint for managing subjects in a study."""

import inspect
from typing import Any, Dict, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.subjects import Subject
from imednet.utils.filters import build_filter_string


class SubjectsEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with subjects in an iMedNet study.

    Provides methods to list and retrieve individual subjects.
    """

    PATH = "/api/v1/edc/studies"

    def _list_impl(
        self,
        client: Any,
        paginator_cls: type[Any],
        *,
        study_key: Optional[str] = None,
        **filters: Any,
    ) -> Any:
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(filters.get("studyKey", ""), "subjects")
        paginator = paginator_cls(client, path, params=params)

        if hasattr(paginator, "__aiter__"):

            async def _collect() -> List[Subject]:
                return [Subject.from_json(item) async for item in paginator]

            return _collect()

        return [Subject.from_json(item) for item in paginator]

    def _get_impl(
        self, client: Any, paginator_cls: type[Any], study_key: str, subject_key: str
    ) -> Any:
        result = self._list_impl(
            client,
            paginator_cls,
            study_key=study_key,
            subjectKey=subject_key,
        )

        if inspect.isawaitable(result):

            async def _await() -> Subject:
                items = await result
                if not items:
                    raise ValueError(f"Subject {subject_key} not found in study {study_key}")
                return items[0]

            return _await()

        if not result:
            raise ValueError(f"Subject {subject_key} not found in study {study_key}")
        return result[0]

    def list(self, study_key: Optional[str] = None, **filters) -> List[Subject]:
        """List subjects in a study with optional filtering."""
        result = self._list_impl(
            self._client,
            Paginator,
            study_key=study_key,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[Subject]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        result = await self._list_impl(
            self._async_client,
            AsyncPaginator,
            study_key=study_key,
            **filters,
        )
        return result

    def get(self, study_key: str, subject_key: str) -> Subject:
        """
        Get a specific subject by key.

        The ``subject_key`` is passed as a filter to :meth:`list`.

        Args:
            study_key: Study identifier
            subject_key: Subject identifier

        Returns:
            Subject object
        """
        result = self._get_impl(self._client, Paginator, study_key, subject_key)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, subject_key: str) -> Subject:
        """Asynchronous version of :meth:`get`.

        This call also filters :meth:`async_list` by ``subject_key``.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client,
            AsyncPaginator,
            study_key,
            subject_key,
        )
