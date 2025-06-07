from unittest.mock import Mock, patch

import pytest
from imednet.endpoints.helpers import build_paginator
from imednet.endpoints.studies import StudiesEndpoint


@pytest.fixture
def mock_endpoint():
    client = Mock()
    ctx = Mock()
    return StudiesEndpoint(client, ctx)


@patch("imednet.endpoints.studies.Paginator")
@patch("imednet.endpoints.studies.Study")
@patch("imednet.endpoints.studies.build_paginator", wraps=build_paginator)
def test_list_with_filters(mock_builder, mock_study, mock_paginator, mock_endpoint):
    mock_paginator.return_value = [{"id": 1}, {"id": 2}]
    mock_study.model_validate.side_effect = lambda x: x

    result = mock_endpoint.list(foo="bar")
    mock_builder.assert_called_once()
    assert mock_paginator.called
    assert result == [{"id": 1}, {"id": 2}]
    assert mock_study.model_validate.call_count == 2


@patch("imednet.endpoints.studies.Paginator")
@patch("imednet.endpoints.studies.Study")
def test_list_without_filters(mock_study, mock_paginator, mock_endpoint):
    mock_paginator.return_value = [{"id": 1}]
    mock_study.model_validate.side_effect = lambda x: x

    result = mock_endpoint.list()
    assert result == [{"id": 1}]
    assert mock_study.model_validate.call_count == 1


@patch("imednet.endpoints.studies.Study")
def test_get_returns_study(mock_study, mock_endpoint):
    mock_study.model_validate.return_value = {"id": "STUDY1"}
    mock_endpoint._client.get.return_value.json.return_value = {"data": [{"id": "STUDY1"}]}
    result = mock_endpoint.get("STUDY1")
    assert result == {"id": "STUDY1"}
    mock_study.model_validate.assert_called_once_with({"id": "STUDY1"})


def test_get_raises_value_error_if_not_found(mock_endpoint):
    mock_endpoint._client.get.return_value.json.return_value = {"data": []}
    with pytest.raises(ValueError, match="Study STUDY2 not found"):
        mock_endpoint.get("STUDY2")
