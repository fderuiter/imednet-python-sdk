"""Endpoint for managing records (eCRF instances) in a study."""

import inspect
from typing import Any, Dict, List, Optional, Union

from imednet.core.paginator import AsyncPaginator, Paginator  # noqa: F401
from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.jobs import Job
from imednet.models.records import Record
from imednet.validation.cache import SchemaCache, validate_record_data


class RecordsEndpoint(ListGetEndpoint):
    """
    API endpoint for interacting with records (eCRF instances) in an iMedNet study.

    Provides methods to list, retrieve, and create records.
    """

    PATH = "records"
    MODEL = Record
    _id_param = "recordId"
    _pop_study_filter = False

    def _create_impl(
        self,
        client: Any,
        *,
        study_key: str,
        records_data: List[Dict[str, Any]],
        email_notify: Union[bool, str, None] = None,
    ) -> Any:
        path = self._build_path(study_key, self.PATH)
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

    def list(  # type: ignore[override]
        self, study_key: Optional[str] = None, record_data_filter: Optional[str] = None, **filters
    ) -> List[Record]:
        """List records in a study with optional filtering."""
        result = self._list_common(
            False,
            study_key=study_key,
            record_data_filter=record_data_filter,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(  # type: ignore[override]
        self,
        study_key: Optional[str] = None,
        record_data_filter: Optional[str] = None,
        **filters: Any,
    ) -> List[Record]:
        """Asynchronous version of :meth:`list`."""
        result = await self._list_common(
            True,
            study_key=study_key,
            record_data_filter=record_data_filter,
            **filters,
        )
        return result

    def get(self, study_key: str, record_id: Union[str, int]) -> Record:  # type: ignore[override]
        """Get a specific record by ID."""
        result = self._list_common(False, study_key=study_key, recordId=record_id)
        if inspect.isawaitable(result):
            raise RuntimeError("Unexpected awaitable result")
        if not result:
            raise ValueError(f"Record {record_id} not found in study {study_key}")
        return result[0]

    async def async_get(self, study_key: str, record_id: Union[str, int]) -> Record:  # type: ignore[override]
        """Asynchronous version of :meth:`get`.

        This method also filters :meth:`async_list` by ``record_id``.
        """
        result = await self._list_common(True, study_key=study_key, recordId=record_id)
        if not result:
            raise ValueError(f"Record {record_id} not found in study {study_key}")
        return result[0]

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
        self._require_async_client()
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

    def _list_impl(
        self,
        client: Any,
        paginator_cls: type[Any],
        *,
        study_key: Optional[str] = None,
        record_data_filter: Optional[str] = None,
        **filters: Any,
    ) -> Any:
        extra = {"recordDataFilter": record_data_filter} if record_data_filter else None
        return super()._list_impl(
            client,
            paginator_cls,
            study_key=study_key,
            extra_params=extra,
            **filters,
        )
