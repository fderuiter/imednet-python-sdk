from unittest.mock import AsyncMock, MagicMock
from imednet.sdk import AsyncImednetSDK

import pytest
from imednet.models.queries import Query
from imednet.models.records import Record
from imednet.models.subjects import Subject
from imednet.models.visits import Visit
from imednet.workflows.subject_data import SubjectDataWorkflow


@pytest.mark.asyncio
async def test_get_all_subject_data_async() -> None:
    sdk = MagicMock()
    sdk.__class__ = AsyncImednetSDK
    sdk.subjects.async_list = AsyncMock(return_value=[Subject(subject_key="S1")])
    sdk.visits.async_list = AsyncMock(return_value=[Visit(visit_id=1, subject_key="S1")])
    sdk.records.async_list = AsyncMock(
        return_value=[Record(record_id=1, subject_key="S1", visit_id=1)]
    )
    sdk.queries.async_list = AsyncMock(return_value=[Query(query_comments=[])])

    wf = SubjectDataWorkflow(sdk)
    data = await wf.get_all_subject_data("STUDY", "S1")

    sdk.subjects.async_list.assert_awaited_once_with("STUDY", subject_key="S1")
    sdk.visits.async_list.assert_awaited_once_with("STUDY", subject_key="S1")
    sdk.records.async_list.assert_awaited_once_with("STUDY", subject_key="S1")
    sdk.queries.async_list.assert_awaited_once_with("STUDY", subject_key="S1")
    assert data.records[0].record_id == 1
