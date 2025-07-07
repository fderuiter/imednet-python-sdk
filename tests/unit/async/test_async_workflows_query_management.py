from unittest.mock import AsyncMock, MagicMock
from imednet.sdk import AsyncImednetSDK


class FakeAsyncSDK(AsyncImednetSDK):
    def __init__(self) -> None:  # pragma: no cover - simplified
        pass


import pytest
from imednet.models.queries import Query, QueryComment
from imednet.models.subjects import Subject
from imednet.workflows.query_management import QueryManagementWorkflow


def make_query(sequence_closed: list[tuple[int, bool]]) -> Query:
    comments = [QueryComment(sequence=s, closed=c) for s, c in sequence_closed]
    return Query(query_comments=comments)


@pytest.mark.asyncio
async def test_get_open_queries_async() -> None:
    sdk = FakeAsyncSDK()
    sdk.queries = MagicMock()
    q = make_query([(1, False)])
    sdk.queries.async_list = AsyncMock(return_value=[q])
    wf = QueryManagementWorkflow(sdk)
    result = await wf.get_open_queries("STUDY")
    sdk.queries.async_list.assert_awaited_once_with("STUDY")
    assert result == [q]


@pytest.mark.asyncio
async def test_get_queries_by_site_async() -> None:
    sdk = FakeAsyncSDK()
    sdk.subjects = MagicMock()
    sdk.queries = MagicMock()
    sdk.subjects.async_list = AsyncMock(return_value=[Subject(subject_key="S1")])
    q = make_query([(1, False)])
    sdk.queries.async_list = AsyncMock(return_value=[q])
    wf = QueryManagementWorkflow(sdk)
    result = await wf.get_queries_by_site("STUDY", "SITE")
    sdk.subjects.async_list.assert_awaited_once_with("STUDY", site_name="SITE")
    sdk.queries.async_list.assert_awaited_once()
    assert result == [q]
