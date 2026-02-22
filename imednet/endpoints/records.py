"""Endpoint for managing records (eCRF instances) in a study."""

from typing import Any, Dict, List, Optional, Tuple, Union

from imednet.constants import HEADER_EMAIL_NOTIFY
from imednet.core.endpoint.mixins import CreateEndpointMixin, EdcListGetEndpoint
from imednet.core.protocols import ParamProcessor
from imednet.models.jobs import Job
from imednet.models.records import Record
from imednet.utils.security import validate_header_value
from imednet.validation.cache import SchemaCache, validate_records_batch


class RecordsParamProcessor(ParamProcessor):
    """Parameter processor for Records endpoint."""

    def process_filters(self, filters: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extract 'record_data_filter' parameter.

        Args:
            filters: The filters dictionary.

        Returns:
            Tuple of (cleaned filters, special parameters).
        """
        filters = filters.copy()
        record_data_filter = filters.pop("record_data_filter", None)
        special_params = {}
        if record_data_filter:
            special_params["recordDataFilter"] = record_data_filter
        return filters, special_params


class RecordsEndpoint(EdcListGetEndpoint[Record], CreateEndpointMixin[Job]):
    """
    API endpoint for interacting with records (eCRF instances) in an iMedNet study.

    Provides methods to list, retrieve, and create records.
    """

    PATH = "records"
    MODEL = Record
    _id_param = "recordId"
    _pop_study_filter = False
    PARAM_PROCESSOR_CLS = RecordsParamProcessor

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
        if schema:
            validate_records_batch(schema, records_data)

        headers = {}
        if email_notify is not None:
            if isinstance(email_notify, str):
                validate_header_value("email_notify", email_notify)
                headers[HEADER_EMAIL_NOTIFY] = email_notify
            else:
                headers[HEADER_EMAIL_NOTIFY] = str(email_notify).lower()

        path = self._build_path(study_key, self.PATH)
        client = self._require_sync_client()
        return self._create_sync(
            client,
            path,
            json=records_data,
            headers=headers,
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
        if schema:
            validate_records_batch(schema, records_data)

        headers = {}
        if email_notify is not None:
            if isinstance(email_notify, str):
                validate_header_value("email_notify", email_notify)
                headers[HEADER_EMAIL_NOTIFY] = email_notify
            else:
                headers[HEADER_EMAIL_NOTIFY] = str(email_notify).lower()

        path = self._build_path(study_key, self.PATH)
        client = self._require_async_client()
        return await self._create_async(
            client,
            path,
            json=records_data,
            headers=headers,
            parse_func=Job.from_json,
        )
