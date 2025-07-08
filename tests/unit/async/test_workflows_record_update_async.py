import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from imednet.models.jobs import Job
from imednet.models.variables import Variable
from imednet.workflows.record_update import RecordUpdateWorkflow


@pytest.mark.asyncio
async def test_async_create_or_update_records_refresh_and_validate() -> None:
    sdk = MagicMock()
    sdk._async_client = object()
    sdk.records.async_create = AsyncMock(return_value=Job(batch_id="1", state="PROCESSING"))
    sdk.jobs.async_get = AsyncMock()
    sdk.variables.async_list = AsyncMock(
        return_value=[
            Variable(
                variable_name="age",
                variable_type="integer",
                form_id=1,
                form_key="F1",
            )
        ]
    )

    wf = RecordUpdateWorkflow(sdk)
    wf._validator.refresh = AsyncMock()  # type: ignore[method-assign]
    wf._validator.validate_batch = AsyncMock()  # type: ignore[method-assign]

    await wf.async_create_or_update_records("STUDY", [{"formKey": "F1", "data": {"age": 5}}])

    wf._validator.refresh.assert_awaited_once_with("STUDY")
    wf._validator.validate_batch.assert_awaited_once_with(
        "STUDY",
        [{"formKey": "F1", "data": {"age": 5}}],
    )
    sdk.records.async_create.assert_awaited_once_with(
        "STUDY",
        [{"formKey": "F1", "data": {"age": 5}}],
        schema=wf._schema,
    )


@pytest.mark.asyncio
async def test_async_create_or_update_records_wait_for_completion(monkeypatch) -> None:
    sdk = MagicMock()
    sdk._async_client = object()
    initial_job = Job(batch_id="1", state="PROCESSING")
    completed_job = Job(batch_id="1", state="COMPLETED")
    sdk.records.async_create = AsyncMock(return_value=initial_job)
    sdk.jobs.async_get = AsyncMock(side_effect=[initial_job, completed_job])
    sdk.variables.async_list = AsyncMock(return_value=[])

    wf = RecordUpdateWorkflow(sdk)
    wf._validator.refresh = AsyncMock()  # type: ignore[method-assign]
    wf._validator.validate_batch = AsyncMock()  # type: ignore[method-assign]
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())

    result = await wf.async_create_or_update_records(
        "STUDY",
        [{"formKey": "F1", "data": {}}],
        wait_for_completion=True,
        poll_interval=0,
        timeout=5,
    )

    sdk.records.async_create.assert_awaited_once_with(
        "STUDY",
        [{"formKey": "F1", "data": {}}],
        schema=wf._schema,
    )
    sdk.jobs.async_get.assert_awaited_with("STUDY", "1")
    assert result.state == "COMPLETED"
