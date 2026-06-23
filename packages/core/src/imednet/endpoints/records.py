"""Endpoint for managing records (eCRF instances) in a study."""

from typing import Awaitable, List, Optional, Union, overload

from imednet.core.endpoint.edc_mixin import ClientT, EdcListGetEndpoint
from imednet.core.endpoint.operations import RecordCreateOperation
from imednet.core.endpoint.strategies import MappingParamProcessor
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.models.jobs import Job
from imednet.models.records import Record
from imednet.utils.typing import JsonDict
from imednet.validation.cache import SchemaCache


class RecordsOperationDef:
    """TODO: Add docstring."""

    PATH = "records"
    MODEL = Record
    _id_param = "recordId"
    PARAM_PROCESSOR = MappingParamProcessor({"record_data_filter": "recordDataFilter"})

    def _create_operation(
        self,
        study_key: str,
        records_data: List[JsonDict],
        email_notify: Union[bool, str, None] = None,
        *,
        schema: Optional[SchemaCache] = None,
    ) -> RecordCreateOperation[Job]:
        """TODO: Add docstring."""
        path = self._get_endpoint_path(study_key)  # type: ignore
        return RecordCreateOperation[Job](
            path=path,
            records_data=records_data,
            email_notify=email_notify,
            schema=schema,
        )


class RecordsEndpoint(RecordsOperationDef, EdcListGetEndpoint[Record, ClientT]):  # type: ignore[misc]
    """API endpoint for interacting with records (eCRF instances)."""

    @overload
    def create(
        self: "RecordsEndpoint[RequestorProtocol]",
        study_key: str,
        records_data: List[JsonDict],
        email_notify: Union[bool, str, None] = None,
        *,
        schema: Optional[SchemaCache] = None,
    ) -> Job: ...

    @overload
    def create(
        self: "RecordsEndpoint[AsyncRequestorProtocol]",
        study_key: str,
        records_data: List[JsonDict],
        email_notify: Union[bool, str, None] = None,
        *,
        schema: Optional[SchemaCache] = None,
    ) -> Awaitable[Job]: ...

    def create(
        self,
        study_key: str,
        records_data: List[JsonDict],
        email_notify: Union[bool, str, None] = None,
        *,
        schema: Optional[SchemaCache] = None,
    ) -> Union[Job, Awaitable[Job]]:
        """TODO: Add docstring."""
        operation = self._create_operation(study_key, records_data, email_notify, schema=schema)
        if self._async_client:
            return operation.execute_async(self._require_async_client(), parse_func=Job.from_json)
        else:
            return operation.execute_sync(self._require_sync_client(), parse_func=Job.from_json)

    async def async_create(  # pragma: no cover
        self,
        study_key: str,
        records_data: List[JsonDict],
        email_notify: Union[bool, str, None] = None,
        *,
        schema: Optional[SchemaCache] = None,
    ) -> Job:
        """Alias for create()."""
        import warnings

        warnings.warn("async_create is deprecated, use create()", DeprecationWarning, stacklevel=2)
        result = self.create(study_key, records_data, email_notify, schema=schema)  # type: ignore[misc,return-value]
        return await result if hasattr(result, "__await__") else result  # type: ignore


class AsyncRecordsEndpoint(RecordsEndpoint):  # type: ignore[misc]
    """Legacy backwards-compatible async endpoint."""

    def __init__(self, client, ctx=None):
        """TODO: Add docstring."""
        super().__init__(client, ctx=ctx)
        self._async_client = client
