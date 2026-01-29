"""Endpoint for managing records (eCRF instances) in a study."""

from typing import Any, Dict, List, Optional, Union

from imednet.constants import HEADER_EMAIL_NOTIFY
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

    def _validate_records_if_schema_present(
        self, schema: Optional[SchemaCache], records_data: List[Dict[str, Any]]
    ) -> None:
        """
        Validate records against schema if provided.

        Args:
            schema: Optional schema cache for validation
            records_data: List of record data to validate
        """
        if schema is not None:
            for rec in records_data:
                fk = rec.get("formKey") or rec.get("form_key")
                if not fk:
                    fid = rec.get("formId") or rec.get("form_id") or 0
                    fk = schema.form_key_from_id(fid)
                if fk:
                    validate_record_data(schema, fk, rec.get("data", {}))

    def _build_headers(self, email_notify: Union[bool, str, None]) -> Dict[str, str]:
        """
        Build headers for record creation request.

        Args:
            email_notify: Email notification setting

        Returns:
            Dictionary of headers

        Raises:
            ValueError: If email_notify contains newlines (header injection prevention)
        """
        headers = {}
        if email_notify is not None:
            if isinstance(email_notify, str):
                # Security: Prevent header injection via newlines
                if "\n" in email_notify or "\r" in email_notify:
                    raise ValueError("email_notify must not contain newlines")
                headers[HEADER_EMAIL_NOTIFY] = email_notify
            else:
                headers[HEADER_EMAIL_NOTIFY] = str(email_notify).lower()
        return headers

    def _prepare_create_request(
        self,
        study_key: str,
        records_data: List[Dict[str, Any]],
        email_notify: Union[bool, str, None],
        schema: Optional[SchemaCache],
    ) -> tuple[str, Dict[str, str]]:
        self._validate_records_if_schema_present(schema, records_data)
        headers = self._build_headers(email_notify)
        path = self._build_path(study_key, self.PATH)
        return path, headers

    def create(
        self,
        study_key: str,
        records_data: List[Dict[str, Any]],
        email_notify: Union[bool, str, None] = None,
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

        Raises:
            ValueError: If email_notify contains invalid characters
        """
        path, headers = self._prepare_create_request(study_key, records_data, email_notify, schema)
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
        """
        Asynchronously create new records in a study.

        This is the async variant of :meth:`create`.

        Args:
            study_key: Study identifier
            records_data: List of record data objects to create
            email_notify: Whether to send email notifications (True/False), or an
                email address as a string.
            schema: Optional :class:`SchemaCache` instance used for local
                validation.

        Returns:
            Job object with information about the created job

        Raises:
            ValueError: If email_notify contains invalid characters
        """
        client = self._require_async_client()
        path, headers = self._prepare_create_request(study_key, records_data, email_notify, schema)
        response = await client.post(path, json=records_data, headers=headers)
        return Job.from_json(response.json())

    def _extract_special_params(self, params: Dict[str, Any], filters: Dict[str, Any]) -> None:
        if "record_data_filter" in filters:
            val = filters.pop("record_data_filter")
            if val:
                params["recordDataFilter"] = val
