from unittest.mock import AsyncMock, MagicMock
from imednet.sdk import AsyncImednetSDK


class FakeAsyncSDK(AsyncImednetSDK):
    def __init__(self) -> None:  # pragma: no cover - simplified
        pass


import pytest
from imednet.models.jobs import Job
from imednet.models.records import RegisterSubjectRequest
from imednet.workflows.register_subjects import RegisterSubjectsWorkflow


@pytest.mark.asyncio
async def test_register_subjects_async() -> None:
    sdk = FakeAsyncSDK()
    sdk.records = MagicMock()
    job = Job(batch_id="1", state="PROCESSING")
    sdk.records.async_create = AsyncMock(return_value=job)
    wf = RegisterSubjectsWorkflow(sdk)
    req = RegisterSubjectRequest(form_key="F", site_name="SITE")
    result = await wf.register_subjects("STUDY", [req])
    sdk.records.async_create.assert_awaited_once()
    assert result == job
