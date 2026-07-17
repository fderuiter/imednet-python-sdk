"""Endpoint for managing records (eCRF instances) in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.core.endpoint.operations import RecordCreateOperation
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

    def _create_operation(
        self,
        study_key: str,
        records_data: list[JsonDict],
        email_notify: bool | str | None = None,
        *,
        schema: SchemaCache | None = None,
    ) -> RecordCreateOperation[Job]:
        """Create a RecordCreateOperation.

        Args:
            study_key: The study key.
            records_data: The data for the records to create.
            email_notify: Whether to send email notifications.
            schema: Optional schema cache for validation.

        Returns:
            The create operation.
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

    def create(
        self,
        study_key: str,
        records_data: list[JsonDict],
        email_notify: bool | str | None = None,
        *,
        schema: SchemaCache | None = None,
    ) -> Job:
        """Create one or more records in a study.

        Args:
            study_key: The study key.
            records_data: The data for the records to create.
            email_notify: Whether to send email notifications.
            schema: Optional schema cache for validation.

        Returns:
            The background job for the creation operation.
        """
        return self._create_operation(
            study_key, records_data, email_notify, schema=schema
        ).execute_sync(self._require_sync_client(), parse_func=Job.from_json)


class AsyncRecordsEndpoint(RecordsOperationDef, EdcAsyncListGetEndpoint[Record]):  # type: ignore[misc]
    """Async API endpoint for interacting with records (eCRF instances)."""

    async def async_create(
        self,
        study_key: str,
        records_data: list[JsonDict],
        email_notify: bool | str | None = None,
        *,
        schema: SchemaCache | None = None,
    ) -> Job:
        """Create one or more records in a study asynchronously.

        Args:
            study_key: The study key.
            records_data: The data for the records to create.
            email_notify: Whether to send email notifications.
            schema: Optional schema cache for validation.

        Returns:
            The background job for the creation operation.
        """
        return await self._create_operation(
            study_key, records_data, email_notify, schema=schema
        ).execute_async(self._require_async_client(), parse_func=Job.from_json)
