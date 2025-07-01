"""Endpoint for managing records (eCRF instances) in a study."""

import inspect
from typing import Any, Dict, List, Optional, Union

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.models.jobs import Job
from imednet.models.records import Record
from imednet.validation.schema import SchemaCache, validate_record_data


class RecordsEndpoint(PagedEndpointMixin):
    """API endpoint for interacting with records in an iMedNet study."""

    PATH = "/api/v1/edc/studies"
    MODEL = Record
    PATH_SUFFIX = "records"
    ID_FILTER = "recordId"
    INCLUDE_STUDY_IN_FILTER = True

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
        self,
        study_key: Optional[str] = None,
        record_data_filter: Optional[str] = None,
        **filters: Any,
    ) -> List[Record]:
        """List records in a study with optional filtering."""
        if record_data_filter is not None:
            filters["record_data_filter"] = record_data_filter
        result = self._list_impl(
            self._client,
            Paginator,
            study_key=study_key,
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
        if record_data_filter is not None:
            filters["record_data_filter"] = record_data_filter
        result = await self._list_impl(
            self._async_client,
            AsyncPaginator,
            study_key=study_key,
            **filters,
        )
        return result

    def get(self, study_key: str, record_id: Union[str, int]) -> Record:
        """Get a specific record by ID."""
        result = self._get_impl(self._client, Paginator, record_id, study_key=study_key)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, record_id: Union[str, int]) -> Record:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client, AsyncPaginator, record_id, study_key=study_key
        )

    def create(
        self,
        study_key: str,
        records_data: List[Dict[str, Any]],
        email_notify: Union[bool, str, None] = None,
        *,
        schema: Optional[SchemaCache] = None,
    ) -> Job:
        """Create new records in a study."""
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
