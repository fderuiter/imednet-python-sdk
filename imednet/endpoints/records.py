"""Endpoint for managing records (eCRF instances) in a study."""

from typing import Any, Dict, List, Optional, Union

from imednet.core.paginator import Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.jobs import Job
from imednet.models.records import Record
from imednet.utils.filters import build_filter_string
from imednet.utils.schema import SchemaCache, validate_record_data


class RecordsEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with records (eCRF instances) in an iMedNet study.

    Provides methods to list, retrieve, and create records.
    """

    path = "/api/v1/edc/studies"

    def list(
        self, study_key: Optional[str] = None, record_data_filter: Optional[str] = None, **filters
    ) -> List[Record]:
        """
        List records in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            record_data_filter: Optional filter for record data fields
            **filters: Additional filter parameters

        Returns:
            List of Record objects
        """
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        if record_data_filter:
            params["recordDataFilter"] = record_data_filter

        path = self._build_path(filters.get("studyKey", ""), "records")
        paginator = Paginator(self._client, path, params=params)
        return [Record.from_json(item) for item in paginator]

    def get(self, study_key: str, record_id: Union[str, int]) -> Record:
        """
        Get a specific record by ID.

        Args:
            study_key: Study identifier
            record_id: Record identifier (can be string or integer)

        Returns:
            Record object
        """
        path = self._build_path(study_key, "records", record_id)
        raw = self._client.get(path).json().get("data", [])
        if not raw:
            raise ValueError(f"Record {record_id} not found in study {study_key}")
        return Record.from_json(raw[0])

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

        path = self._build_path(study_key, "records")
        headers = {}
        if email_notify is not None:
            if isinstance(email_notify, str):
                headers["x-email-notify"] = email_notify  # Use email address directly
            else:
                headers["x-email-notify"] = str(email_notify).lower()  # Use 'true'/'false' for bool

        response = self._client.post(path, json=records_data, headers=headers)
        return Job.from_json(response.json())
