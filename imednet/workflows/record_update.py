"""Placeholder for Record Creation/Update workflows."""

import warnings
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Union

from ..models import Job
from ..validation.cache import SchemaCache, SchemaValidator
from .job_poller import JobPoller

if TYPE_CHECKING:
    from ..sdk import ImednetSDK


class RecordUpdateWorkflow:
    """
    Provides workflows for creating or updating records, including batch submission
    and optional job status monitoring.

    Args:
        sdk: An instance of the ImednetSDK.
    """

    def __init__(self, sdk: "ImednetSDK"):
        self._sdk = sdk
        self._validator = SchemaValidator(sdk)
        from typing import cast

        self._schema: SchemaCache = cast(SchemaCache, self._validator.schema)

    def create_or_update_records(
        self,
        study_key: str,
        records_data: List[Dict[str, Any]],
        wait_for_completion: bool = False,
        timeout: int = 300,
        poll_interval: int = 5,
    ) -> Job:
        """Submit records for creation or update and optionally wait for completion."""

        if records_data:
            first_ref = records_data[0].get("formKey") or self._schema.form_key_from_id(
                records_data[0].get("formId", 0)
            )
            if first_ref and not self._schema.variables_for_form(first_ref):
                self._validator.refresh(study_key)

        self._validator.validate_batch(study_key, records_data)

        job = self._sdk.records.create(study_key, records_data, schema=self._schema)
        if not wait_for_completion:
            return job
        if not job.batch_id:
            raise ValueError("Submission successful but no batch_id received.")
        return JobPoller(self._sdk.jobs.get, False).run(
            study_key,
            job.batch_id,
            poll_interval,
            timeout,
        )

    def submit_record_batch(self, *args: Any, **kwargs: Any) -> Job:  # pragma: no cover
        warnings.warn(
            "submit_record_batch is deprecated; use create_or_update_records",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.create_or_update_records(*args, **kwargs)

    def register_subject(
        self,
        study_key: str,
        form_identifier: Union[str, int],
        site_identifier: Union[str, int],
        data: Dict[str, Any],
        form_identifier_type: Literal["key", "id"] = "key",
        site_identifier_type: Literal["name", "id"] = "name",
        wait_for_completion: bool = False,
        timeout: int = 300,
        poll_interval: int = 5,
    ) -> Job:
        """
        Registers a new subject by submitting a single record.

        Args:
            study_key: The study key.
            form_identifier: The form key or ID.
            site_identifier: The site name or ID.
            data: The dictionary of record data (variable names and values).
            form_identifier_type: Whether `form_identifier` is a 'key' or 'id'.
            site_identifier_type: Whether `site_identifier` is a 'name' or 'id'.
            wait_for_completion: If True, wait for the job to complete.
            timeout: Timeout in seconds for waiting.
            poll_interval: Polling interval in seconds.

        Returns:
            The Job status object.
        """
        record = {
            "formKey" if form_identifier_type == "key" else "formId": form_identifier,
            "siteName" if site_identifier_type == "name" else "siteId": site_identifier,
            "data": data,
        }
        return self.create_or_update_records(
            study_key=study_key,
            records_data=[record],
            wait_for_completion=wait_for_completion,
            timeout=timeout,
            poll_interval=poll_interval,
        )

    def update_scheduled_record(
        self,
        study_key: str,
        form_identifier: Union[str, int],
        subject_identifier: Union[str, int],
        interval_identifier: Union[str, int],
        data: Dict[str, Any],
        form_identifier_type: Literal["key", "id"] = "key",
        subject_identifier_type: Literal["key", "id", "oid"] = "key",
        interval_identifier_type: Literal["name", "id"] = "name",
        wait_for_completion: bool = False,
        timeout: int = 300,
        poll_interval: int = 5,
    ) -> Job:
        """
        Updates an existing scheduled record for a subject.

        Args:
            study_key: The study key.
            form_identifier: The form key or ID.
            subject_identifier: The subject key, ID, or OID.
            interval_identifier: The interval name or ID.
            data: The dictionary of record data (variable names and values).
            form_identifier_type: Whether `form_identifier` is a 'key' or 'id'.
            subject_identifier_type: Whether `subject_identifier` is a 'key', 'id', or 'oid'.
            interval_identifier_type: Whether `interval_identifier` is a 'name' or 'id'.
            wait_for_completion: If True, wait for the job to complete.
            timeout: Timeout in seconds for waiting.
            poll_interval: Polling interval in seconds.

        Returns:
            The Job status object.
        """
        subject_id_field_map = {"key": "subjectKey", "id": "subjectId", "oid": "subjectOid"}
        record = {
            "formKey" if form_identifier_type == "key" else "formId": form_identifier,
            subject_id_field_map[subject_identifier_type]: subject_identifier,
            (
                "intervalName" if interval_identifier_type == "name" else "intervalId"
            ): interval_identifier,
            "data": data,
        }
        return self.create_or_update_records(
            study_key=study_key,
            records_data=[record],
            wait_for_completion=wait_for_completion,
            timeout=timeout,
            poll_interval=poll_interval,
        )

    def create_new_record(
        self,
        study_key: str,
        form_identifier: Union[str, int],
        subject_identifier: Union[str, int],
        data: Dict[str, Any],
        form_identifier_type: Literal["key", "id"] = "key",
        subject_identifier_type: Literal["key", "id", "oid"] = "key",
        wait_for_completion: bool = False,
        timeout: int = 300,
        poll_interval: int = 5,
    ) -> Job:
        """
        Creates a new (unscheduled) record for an existing subject.

        Args:
            study_key: The study key.
            form_identifier: The form key or ID.
            subject_identifier: The subject key, ID, or OID.
            data: The dictionary of record data (variable names and values).
            form_identifier_type: Whether `form_identifier` is a 'key' or 'id'.
            subject_identifier_type: Whether `subject_identifier` is a 'key', 'id', or 'oid'.
            wait_for_completion: If True, wait for the job to complete.
            timeout: Timeout in seconds for waiting.
            poll_interval: Polling interval in seconds.

        Returns:
            The Job status object.
        """
        subject_id_field_map = {"key": "subjectKey", "id": "subjectId", "oid": "subjectOid"}
        record = {
            "formKey" if form_identifier_type == "key" else "formId": form_identifier,
            subject_id_field_map[subject_identifier_type]: subject_identifier,
            "data": data,
        }
        return self.create_or_update_records(
            study_key=study_key,
            records_data=[record],
            wait_for_completion=wait_for_completion,
            timeout=timeout,
            poll_interval=poll_interval,
        )


# Integration:
# - Accessed via the main SDK instance
#       (e.g., `sdk.workflows.record_update.create_or_update_records(...)`).
# - Simplifies the process of submitting data and optionally monitoring the asynchronous job.
