"""Endpoint for managing records (eCRF instances) in a study."""

import inspect
from typing import Any, Dict, List, Optional, Union

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.jobs import Job
from imednet.models.records import Record
from imednet.utils.filters import build_filter_string
from imednet.validation.cache import SchemaCache, validate_record_data


class RecordsEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with records (eCRF instances) in an iMedNet study.

    Provides methods to list, retrieve, and create records.
    """

    PATH = "/api/v1/edc/studies"

    def _list_impl(
        self,
        client: Any,
        paginator_cls: type[Any],
        *,
        study_key: Optional[str] = None,
        record_data_filter: Optional[str] = None,
        **filters: Any,
    ) -> Any:
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)
        if record_data_filter:
            params["recordDataFilter"] = record_data_filter

        path = self._build_path(filters.get("studyKey", ""), "records")
        paginator = paginator_cls(client, path, params=params)

        if hasattr(paginator, "__aiter__"):

            async def _collect() -> List[Record]:
                return [Record.from_json(item) async for item in paginator]

            return _collect()

        return [Record.from_json(item) for item in paginator]

    def _get_impl(
        self, client: Any, paginator_cls: type[Any], study_key: str, record_id: Union[str, int]
    ) -> Any:
        result = self._list_impl(
            client,
            paginator_cls,
            study_key=study_key,
            recordId=record_id,
        )

        if inspect.isawaitable(result):

            async def _await() -> Record:
                items = await result
                if not items:
                    raise ValueError(f"Record {record_id} not found in study {study_key}")
                return items[0]

            return _await()

        if not result:
            raise ValueError(f"Record {record_id} not found in study {study_key}")
        return result[0]

    def _create_impl(
        self,
        client: Any,
        *,
        study_key: str,
        records_data: List[Dict[str, Any]],
        email_notify: Union[bool, str, None] = None,
    ) -> Any:
        path = self._build_path(study_key, "records")
        headers = {}
        if email_notify is not None:
            if isinstance(email_notify, str):
                headers["x-email-notify"] = email_notify
            else:
                headers["x-email-notify"] = str(email_notify).lower()

        if inspect.iscoroutinefunction(client.post):

            async def _async() -> Job:
                response = await client.post(path, json=records_data, headers=headers)
                return Job.from_json(response.json())

            return _async()

        response = client.post(path, json=records_data, headers=headers)
        return Job.from_json(response.json())

    def list(
        self, study_key: Optional[str] = None, record_data_filter: Optional[str] = None, **filters
    ) -> List[Record]:
        """List records in a study with optional filtering."""
        result = self._list_impl(
            self._client,
            Paginator,
            study_key=study_key,
            record_data_filter=record_data_filter,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(
        self,
        study_key: Optional[str] = None,
        record_data_filter: Optional[str] = None,
        **filters: Any,
    ) -> List[Record]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        result = await self._list_impl(
            self._async_client,
            AsyncPaginator,
            study_key=study_key,
            record_data_filter=record_data_filter,
            **filters,
        )
        return result

    def get(self, study_key: str, record_id: Union[str, int]) -> Record:
        """
        Get a specific record by ID.

        ``record_id`` is provided to :meth:`list` as a filter value.

        Args:
            study_key: Study identifier
            record_id: Record identifier (can be string or integer)

        Returns:
            Record object
        """
        result = self._get_impl(self._client, Paginator, study_key, record_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, record_id: Union[str, int]) -> Record:
        """Asynchronous version of :meth:`get`.

        This method also filters :meth:`async_list` by ``record_id``.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(self._async_client, AsyncPaginator, study_key, record_id)

    def create(
        self,
        study_key: str,
        records_data: List[Dict[str, Any]],
        email_notify: Union[bool, str, None] = None,  # Accept bool, str (email), or None
        *,
        schema: Optional[SchemaCache] = None,
    ) -> Job:
        """
        Create new records in a study.

        Args:
            study_key: Study identifier
            records_data: List of record data objects to create
            email_notify: Whether to send email notifications (True/False), or an
                email address as a string.
            schema: Optional :class:`SchemaCache` instance used for local
                validation.

        Returns:
            Job object with information about the created job
        """
        if schema is not None:
            for rec in records_data:
                fk = rec.get("formKey") or schema.form_key_from_id(rec.get("formId", 0))
                if fk:
                    validate_record_data(schema, fk, rec.get("data", {}))

        result = self._create_impl(
            self._client,
            study_key=study_key,
            records_data=records_data,
            email_notify=email_notify,
        )
        return result  # type: ignore[return-value]

    async def async_create(
        self,
        study_key: str,
        records_data: List[Dict[str, Any]],
        email_notify: Union[bool, str, None] = None,
        *,
        schema: Optional[SchemaCache] = None,
    ) -> Job:
        """Asynchronous version of :meth:`create`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        if schema is not None:
            for rec in records_data:
                fk = rec.get("formKey") or schema.form_key_from_id(rec.get("formId", 0))
                if fk:
                    validate_record_data(schema, fk, rec.get("data", {}))

        return await self._create_impl(
            self._async_client,
            study_key=study_key,
            records_data=records_data,
            email_notify=email_notify,
        )
