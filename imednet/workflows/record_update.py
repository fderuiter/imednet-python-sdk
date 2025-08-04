"""Utilities for submitting and updating records in iMedNet studies."""

import asyncio
import inspect
import time
import warnings
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Literal, Union, cast

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
        if getattr(sdk, "_async_client", None) is None:
            self._validator._is_async = False

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

        return asyncio.run(
            self._create_or_update_common(
                study_key,
                records_data,
                wait_for_completion,
                timeout,
                poll_interval,
                is_async=False,
            )
        )

    async def async_create_or_update_records(
        self,
        study_key: str,
        records_data: List[Dict[str, Any]],
        wait_for_completion: bool = False,
        timeout: int = 300,
        poll_interval: int = 5,
    ) -> Job:
        """Asynchronous variant of :meth:`create_or_update_records`."""

        return await self._create_or_update_common(
            study_key,
            records_data,
            wait_for_completion,
            timeout,
            poll_interval,
            is_async=True,
        )

    async def _create_or_update_common(
        self,
        study_key: str,
        records_data: List[Dict[str, Any]],
        wait_for_completion: bool,
        timeout: int,
        poll_interval: int,
        *,
        is_async: bool,
    ) -> Job:
        """Shared logic for submitting records synchronously or asynchronously."""

        if records_data:
            first_ref = records_data[0].get("formKey") or self._schema.form_key_from_id(
                records_data[0].get("formId", 0)
            )
            if first_ref and not self._schema.variables_for_form(first_ref):
                result = self._validator.refresh(study_key)
                if inspect.isawaitable(result):
                    await result
                if first_ref not in self._schema.forms:
                    raise ValueError(f"Form key '{first_ref}' not found")

        result = self._validator.validate_batch(study_key, records_data)
        if inspect.isawaitable(result):
            await result

        if is_async:
            job = await self._sdk.records.async_create(study_key, records_data, schema=self._schema)
        else:
            job = self._sdk.records.create(study_key, records_data, schema=self._schema)

        if not wait_for_completion:
            return job
        if not job.batch_id:
            raise ValueError("Submission successful but no batch_id received.")

        poller = JobPoller(self._sdk.jobs.async_get if is_async else self._sdk.jobs.get, is_async)
        sleep_fn = asyncio.sleep if is_async else time.sleep
        return await poller._run_common(
            study_key,
            job.batch_id,
            poller._get_job,
            cast(Callable[[float], Any], sleep_fn),
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

    def _build_record_payload(
        self,
        *,
        form_identifier: Union[str, int],
        form_identifier_type: Literal["key", "id"] = "key",
        data: Dict[str, Any],
        subject_identifier: Union[str, int, None] = None,
        subject_identifier_type: Literal["key", "id", "oid"] = "key",
        site_identifier: Union[str, int, None] = None,
        site_identifier_type: Literal["name", "id"] = "name",
        interval_identifier: Union[str, int, None] = None,
        interval_identifier_type: Literal["name", "id"] = "name",
    ) -> Dict[str, Any]:
        """Return a record payload for ``create_or_update_records``."""

        record: Dict[str, Any] = {
            "formKey" if form_identifier_type == "key" else "formId": form_identifier,
            "data": data,
        }

        if subject_identifier is not None:
            subject_id_field_map = {
                "key": "subjectKey",
                "id": "subjectId",
                "oid": "subjectOid",
            }
            record[subject_id_field_map[subject_identifier_type]] = subject_identifier

        if site_identifier is not None:
            record["siteName" if site_identifier_type == "name" else "siteId"] = site_identifier

        if interval_identifier is not None:
            record["intervalName" if interval_identifier_type == "name" else "intervalId"] = (
                interval_identifier
            )

        return record

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
        record = self._build_record_payload(
            form_identifier=form_identifier,
            form_identifier_type=form_identifier_type,
            site_identifier=site_identifier,
            site_identifier_type=site_identifier_type,
            data=data,
        )
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
        record = self._build_record_payload(
            form_identifier=form_identifier,
            form_identifier_type=form_identifier_type,
            subject_identifier=subject_identifier,
            subject_identifier_type=subject_identifier_type,
            interval_identifier=interval_identifier,
            interval_identifier_type=interval_identifier_type,
            data=data,
        )
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
        record = self._build_record_payload(
            form_identifier=form_identifier,
            form_identifier_type=form_identifier_type,
            subject_identifier=subject_identifier,
            subject_identifier_type=subject_identifier_type,
            data=data,
        )
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
