from unittest.mock import AsyncMock, MagicMock
from imednet.sdk import AsyncImednetSDK


class FakeAsyncSDK(AsyncImednetSDK):
    def __init__(self) -> None:  # pragma: no cover - simplified
        pass


import pytest
from imednet.models.record_revisions import RecordRevision
from imednet.models.records import Record
from imednet.models.subjects import Subject
from imednet.models.visits import Visit
from imednet.workflows.data_extraction import DataExtractionWorkflow


@pytest.mark.asyncio
async def test_extract_records_by_criteria_async() -> None:
    sdk = FakeAsyncSDK()
    sdk.subjects = MagicMock()
    sdk.visits = MagicMock()
    sdk.records = MagicMock()
    sdk.subjects.async_list = AsyncMock(return_value=[Subject(subject_key="S1")])
    sdk.visits.async_list = AsyncMock(return_value=[Visit(visit_id=1, subject_key="S1")])
    sdk.records.async_list = AsyncMock(
        return_value=[Record(record_id=1, subject_key="S1", visit_id=1)]
    )

    wf = DataExtractionWorkflow(sdk)
    records = await wf.extract_records_by_criteria(
        "STUDY",
        subject_filter={"status": "x"},
        visit_filter={"visit_id": 1},
    )

    sdk.subjects.async_list.assert_awaited_once()
    sdk.visits.async_list.assert_awaited_once()
    sdk.records.async_list.assert_awaited_once()
    assert len(records) == 1


@pytest.mark.asyncio
async def test_extract_audit_trail_async() -> None:
    sdk = FakeAsyncSDK()
    sdk.record_revisions = MagicMock()
    sdk.record_revisions.async_list = AsyncMock(return_value=[RecordRevision(record_revision_id=1)])

    wf = DataExtractionWorkflow(sdk)
    revisions = await wf.extract_audit_trail("STUDY")

    sdk.record_revisions.async_list.assert_awaited_once_with("STUDY")
    assert len(revisions) == 1
