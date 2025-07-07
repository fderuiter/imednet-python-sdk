from unittest.mock import AsyncMock, MagicMock
from imednet.sdk import AsyncImednetSDK


class FakeAsyncSDK(AsyncImednetSDK):
    def __init__(self) -> None:  # pragma: no cover - simplified
        pass


import pytest
from imednet.models.jobs import Job
from imednet.workflows.record_update import RecordUpdateWorkflow


@pytest.mark.asyncio
async def test_create_or_update_records_async_no_wait() -> None:
    sdk = FakeAsyncSDK()
    sdk.records = MagicMock()
    sdk.variables = MagicMock()
    sdk.variables.async_list = AsyncMock(return_value=[])
    job = Job(batch_id="1", state="PROCESSING")
    sdk.records.async_create = AsyncMock(return_value=job)
    wf = RecordUpdateWorkflow(sdk)
    result = await wf.create_or_update_records("S", [{"a": 1}])
    sdk.records.async_create.assert_awaited_once_with("S", [{"a": 1}], schema=wf._schema)
    assert result == job
