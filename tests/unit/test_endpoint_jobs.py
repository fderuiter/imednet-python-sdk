from unittest.mock import Mock, patch

import pytest
from imednet.endpoints.jobs import JobsEndpoint


@pytest.fixture
def mock_endpoint():
    client = Mock()
    ctx = Mock()
    return JobsEndpoint(client, ctx)


@patch("imednet.endpoints.jobs.Job")
def test_get_returns_job(mock_job, mock_endpoint):
    mock_job.from_json.return_value = {"id": "job1"}
    mock_endpoint._client.get.return_value.json.return_value = {"id": "job1"}
    result = mock_endpoint.get("STUDY1", "batch123")
    assert result == {"id": "job1"}
    mock_job.from_json.assert_called_once_with({"id": "job1"})


def test_get_raises_value_error_if_not_found(mock_endpoint):
    mock_endpoint._client.get.return_value.json.return_value = {}
    with pytest.raises(ValueError, match="Job batch123 not found in study STUDY1"):
        mock_endpoint.get("STUDY1", "batch123")
