from unittest.mock import Mock, patch

import pytest
from imednet.endpoints.records import RecordsEndpoint


@pytest.fixture
def endpoint():
    client = Mock()
    ctx = Mock()
    ctx.default_study_key = "DEF"
    return RecordsEndpoint(client, ctx)


@patch("imednet.endpoints.records.Paginator")
@patch("imednet.endpoints.records.Record")
@patch("imednet.endpoints.records.build_filter_string")
def test_list(mock_build, mock_record, mock_pag, endpoint):
    mock_build.return_value = "f=b"
    mock_pag.return_value = [{"id": 1}]
    mock_record.from_json.side_effect = lambda x: x

    result = endpoint.list(study_key="S1", f="b")
    assert result == [{"id": 1}]
    assert mock_build.called
    assert mock_pag.called


@patch("imednet.endpoints.records.Record")
def test_get(mock_record, endpoint):
    endpoint._client.get.return_value.json.return_value = {"data": [{"id": 2}]}
    mock_record.from_json.return_value = {"id": 2}
    result = endpoint.get("S1", 2)
    assert result == {"id": 2}


@patch("imednet.endpoints.records.Job")
def test_create(mock_job, endpoint):
    endpoint._client.post.return_value.json.return_value = {"job": 1}
    mock_job.from_json.return_value = {"job": 1}
    result = endpoint.create("S1", [{"foo": "bar"}], email_notify=True)
    assert result == {"job": 1}
