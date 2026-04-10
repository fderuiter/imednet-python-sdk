"""Endpoint for managing records (eCRF instances) in a study."""

from typing import Any, Dict, List, Optional, Union

from imednet.core.endpoint.base import GenericListGetEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.endpoint.operations import RecordCreateOperation
from imednet.core.endpoint.strategies import MappingParamProcessor
from imednet.models.jobs import Job
from imednet.models.records import Record
from imednet.validation.cache import SchemaCache


class RecordsEndpoint(
    EdcEndpointMixin,
    GenericListGetEndpoint[Record],
):
    """
    API endpoint for interacting with records (eCRF instances) in an iMedNet study.

    Provides methods to list, retrieve, and create records.
    """

    PATH = "records"
    MODEL = Record
    _id_param = "recordId"
    PARAM_PROCESSOR = MappingParamProcessor({"record_data_filter": "recordDataFilter"})

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
        path = self._build_path(study_key, self.PATH)
        operation = RecordCreateOperation[Job](
            path=path,
            records_data=records_data,
            email_notify=email_notify,
            schema=schema,
        )
        return operation.execute_sync(
            self._require_sync_client(),
            parse_func=Job.from_json,
        )

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
        path = self._build_path(study_key, self.PATH)
        operation = RecordCreateOperation[Job](
            path=path,
            records_data=records_data,
            email_notify=email_notify,
            schema=schema,
        )
        return await operation.execute_async(
            self._require_async_client(),
            parse_func=Job.from_json,
        )
