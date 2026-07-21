"""Endpoint for managing records (eCRF instances) in a study."""

from typing import Any
from imednet.core.endpoint.dispatch import execute_operation
from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.core.endpoint.operations.record_create import RecordCreateOperation
from imednet.core.endpoint.strategies import MappingParamProcessor
from imednet.models.jobs import Job
from imednet.models.records import Record
from imednet.utils.typing import JsonDict
from imednet.validation.cache import SchemaCache


class RecordsOperationDef:
    """Definition for Record operations."""

    PATH = "records"
    MODEL = Record
    _id_param = "recordId"
    PARAM_PROCESSOR = MappingParamProcessor({"record_data_filter": "recordDataFilter"})

    @execute_operation  # type: ignore
    def create(
        self,
        study_key: str,
        records_data: list[JsonDict],
        email_notify: bool | str | None = None,
        *,
        schema: SchemaCache | None = None,
    ) -> RecordCreateOperation[Job]:
        """Create one or more records in a study.

        Args:
            study_key: The study key.
            records_data: The data for the records to create.
            email_notify: Whether to send email notifications.
            schema: Optional schema cache for validation.

        Returns:
            The background job for the creation operation.
        """
        path = self._get_endpoint_path(study_key)  # type: ignore
        return RecordCreateOperation[Job](
            path=path,
            records_data=records_data,
            email_notify=email_notify,
            schema=schema,
        )



class RecordsEndpoint(RecordsOperationDef, EdcSyncListGetEndpoint[Record]):  # type: ignore[misc]
    """API endpoint for interacting with records (eCRF instances)."""


class AsyncRecordsEndpoint(RecordsOperationDef, EdcAsyncListGetEndpoint[Record]):  # type: ignore[misc]
    """Async API endpoint for interacting with records (eCRF instances)."""
