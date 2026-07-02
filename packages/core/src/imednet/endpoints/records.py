"""Custom logic mixins for Records endpoint."""

from typing import List, Optional, Union
from imednet.core.endpoint.operations import RecordCreateOperation
from imednet.models.jobs import Job
from imednet.utils.typing import JsonDict
from imednet.validation.cache import SchemaCache

class RecordsMixin:
    def _create_operation(
        self,
        study_key: str,
        records_data: List[JsonDict],
        email_notify: Union[bool, str, None] = None,
        *,
        schema: Optional[SchemaCache] = None,
    ) -> RecordCreateOperation[Job]:
        path = self._get_endpoint_path(study_key)
        return RecordCreateOperation[Job](
            path=path,
            records_data=records_data,
            email_notify=email_notify,
            schema=schema,
        )

    def create(
        self,
        study_key: str,
        records_data: List[JsonDict],
        email_notify: Union[bool, str, None] = None,
        *,
        schema: Optional[SchemaCache] = None,
    ) -> Job:
        return self._create_operation(
            study_key, records_data, email_notify, schema=schema
        ).execute_sync(self._require_sync_client(), parse_func=Job.from_json)

class AsyncRecordsMixin:
    def _create_operation(
        self,
        study_key: str,
        records_data: List[JsonDict],
        email_notify: Union[bool, str, None] = None,
        *,
        schema: Optional[SchemaCache] = None,
    ) -> RecordCreateOperation[Job]:
        path = self._get_endpoint_path(study_key)
        return RecordCreateOperation[Job](
            path=path,
            records_data=records_data,
            email_notify=email_notify,
            schema=schema,
        )

    async def async_create(
        self,
        study_key: str,
        records_data: List[JsonDict],
        email_notify: Union[bool, str, None] = None,
        *,
        schema: Optional[SchemaCache] = None,
    ) -> Job:
        return await self._create_operation(
            study_key, records_data, email_notify, schema=schema
        ).execute_async(self._require_async_client(), parse_func=Job.from_json)
