"""Endpoint for managing records (eCRF instances) in a study."""

from typing import Any, Dict, List, Optional, Union

from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.jobs import Job
from imednet.models.records import Record
from imednet.validation.cache import SchemaCache, validate_record_data


class RecordsEndpoint(ListGetEndpoint[Record]):
    """
    API endpoint for interacting with records (eCRF instances) in an iMedNet study.

    Provides methods to list, retrieve, and create records.
    """

    PATH = "records"
    MODEL = Record
    _id_param = "recordId"
    _pop_study_filter = False

    def _prepare_create_headers(
        self, email_notify: Union[bool, str, None]
    ) -> Dict[str, str]:
        headers = {}
        if email_notify is not None:
            if isinstance(email_notify, str):
                # Security: Prevent header injection via newlines
                if "\n" in email_notify or "\r" in email_notify:
                    raise ValueError("email_notify must not contain newlines")
                headers["x-email-notify"] = email_notify
            else:
                headers["x-email-notify"] = str(email_notify).lower()
        return headers

    def _validate_records_if_schema_present(
        self, schema: Optional[SchemaCache], records_data: List[Dict[str, Any]]
    ) -> None:
        if schema is not None:
            for rec in records_data:
                fk = rec.get("formKey") or rec.get("form_key")
                if not fk:
                    fid = rec.get("formId") or rec.get("form_id") or 0
                    fk = schema.form_key_from_id(fid)
                if fk:
                    validate_record_data(schema, fk, rec.get("data", {}))

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
        self._validate_records_if_schema_present(schema, records_data)
        path = self._build_path(study_key, self.PATH)
        headers = self._prepare_create_headers(email_notify)

        response = self._client.post(path, json=records_data, headers=headers)
        return Job.from_json(response.json())

    async def async_create(
        self,
        study_key: str,
        records_data: List[Dict[str, Any]],
        email_notify: Union[bool, str, None] = None,
        *,
        schema: Optional[SchemaCache] = None,
    ) -> Job:
        """Asynchronous version of :meth:`create`."""
        client = self._require_async_client()
        self._validate_records_if_schema_present(schema, records_data)

        path = self._build_path(study_key, self.PATH)
        headers = self._prepare_create_headers(email_notify)

        response = await client.post(path, json=records_data, headers=headers)
        return Job.from_json(response.json())

    def _process_filters(self, filters: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        record_data_filter = filters.pop("record_data_filter", None)
        extra = {"recordDataFilter": record_data_filter} if record_data_filter else {}
        return filters, extra
