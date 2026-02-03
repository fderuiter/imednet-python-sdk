import pytest
from unittest.mock import Mock, AsyncMock
from typing import List
from imednet.endpoints.subjects import SubjectsEndpoint
from imednet.models.subjects import Subject

@pytest.fixture
def subject_list():
    return [
        Subject(studyKey="sk", subjectId=1, siteId=101, subjectKey="s1"),
        Subject(studyKey="sk", subjectId=2, siteId=102, subjectKey="s2"),
        Subject(studyKey="sk", subjectId=3, siteId=101, subjectKey="s3"),
        Subject(studyKey="sk", subjectId=4, siteId="101", subjectKey="s4"), # String siteId
        Subject(studyKey="sk", subjectId=5, siteId="103", subjectKey="s5"),
    ]

def test_list_by_site_filtering(subject_list):
    # Mock client and context as they are required by __init__ but not used if we mock list
    mock_client = Mock()
    mock_ctx = Mock()

    endpoint = SubjectsEndpoint(mock_client, mock_ctx)
    endpoint.list = Mock(return_value=subject_list)

    # Act
    filtered_int = endpoint.list_by_site("sk", 101)
    filtered_str = endpoint.list_by_site("sk", "101")
    filtered_mismatch = endpoint.list_by_site("sk", 999)

    # Assert
    assert len(filtered_int) == 3
    assert {s.subject_id for s in filtered_int} == {1, 3, 4}

    assert len(filtered_str) == 3
    assert {s.subject_id for s in filtered_str} == {1, 3, 4}

    assert len(filtered_mismatch) == 0

@pytest.mark.asyncio
async def test_async_list_by_site_filtering(subject_list):
    # Mock client and context
    mock_client = Mock()
    mock_ctx = Mock()

    endpoint = SubjectsEndpoint(mock_client, mock_ctx)
    endpoint.async_list = AsyncMock(return_value=subject_list)

    # Act
    filtered_int = await endpoint.async_list_by_site("sk", 101)
    filtered_str = await endpoint.async_list_by_site("sk", "101")
    filtered_mismatch = await endpoint.async_list_by_site("sk", 999)

    # Assert
    assert len(filtered_int) == 3
    assert {s.subject_id for s in filtered_int} == {1, 3, 4}

    assert len(filtered_str) == 3
    assert {s.subject_id for s in filtered_str} == {1, 3, 4}

    assert len(filtered_mismatch) == 0
