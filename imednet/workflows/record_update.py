"""Placeholder for Record Creation/Update workflows."""

import time
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Union

from ..models import Job
from ..validation.schema import SchemaValidator

if TYPE_CHECKING:
    from ..sdk import ImednetSDK

# Define terminal states for job polling
TERMINAL_JOB_STATES = {"COMPLETED", "FAILED", "CANCELLED"}  # Adjust if needed based on API


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
        self._schema = self._validator.schema

    def submit_record_batch(
        self,
        study_key: str,
        records_data: List[Dict[str, Any]],
        wait_for_completion: bool = False,
        timeout: int = 300,
        poll_interval: int = 5,
    ) -> Job:
        """
        Submits a batch of record data for creation or update.

        Optionally waits for the background job to complete by polling its status.

        Args:
            study_key: The key identifying the study.
            records_data: A list of dictionaries, where each dictionary represents
                          a record to be created or updated, matching the API's
                          expected request body structure.
            wait_for_completion: If True, poll the job status until it reaches a
                                 terminal state (e.g., COMPLETED, FAILED) or the
                                 timeout is reached.
            timeout: Maximum time in seconds to wait for job completion if
                     `wait_for_completion` is True.
            poll_interval: Time in seconds between job status checks.

        Returns:
            A Job object representing the initial status or the final status
            if `wait_for_completion` is True.

        Raises:
            TimeoutError: If `wait_for_completion` is True and the job does not
                          complete within the specified timeout.
            # ImednetApiError: If the initial submission or status polling fails.
            # Commented out as not defined here
        """
        if records_data:
            first_ref = records_data[0].get("formKey") or self._schema.form_key_from_id(
                records_data[0].get("formId", 0)
            )
            if first_ref and not self._schema.variables_for_form(first_ref):
                self._validator.refresh(study_key)

        self._validator.validate_batch(study_key, records_data)

        # Call the SDK's records.create method - Pass records_data directly
        initial_job_status = self._sdk.records.create(
            study_key,
            records_data,
            schema=self._schema,
        )

        if not wait_for_completion:
            return initial_job_status

        if not initial_job_status.batch_id:
            # Should not happen if API call was successful, but good practice to check
            raise ValueError("Submission successful but no batch_id received.")

        start_time = time.monotonic()
        batch_id = initial_job_status.batch_id
        current_job_status = initial_job_status

        while True:
            if current_job_status.state.upper() in TERMINAL_JOB_STATES:
                return current_job_status

            elapsed_time = time.monotonic() - start_time
            if elapsed_time >= timeout:
                raise TimeoutError(
                    f"Timeout ({timeout}s) waiting for job batch '{batch_id}' "
                    f"to complete. Last state: {current_job_status.state}"
                )

            # Wait before polling again
            time.sleep(poll_interval)

            # Poll the job status using the batch_id
            # Assuming sdk.jobs.get expects study_key and batch_id
            current_job_status = self._sdk.jobs.get(study_key, batch_id)

        # This line is technically unreachable due to the loop structure but ensures return type
        return current_job_status

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
        return self.submit_record_batch(
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
        return self.submit_record_batch(
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
        return self.submit_record_batch(
            study_key=study_key,
            records_data=[record],
            wait_for_completion=wait_for_completion,
            timeout=timeout,
            poll_interval=poll_interval,
        )


# Integration:
# - Accessed via the main SDK instance
#       (e.g., `sdk.workflows.record_update.submit_record_batch(...)`).
# - Simplifies the process of submitting data and optionally monitoring the asynchronous job.
