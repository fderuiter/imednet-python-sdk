from unittest.mock import Mock, patch

import pytest
from imednet.endpoints.subjects import SubjectsEndpoint


@pytest.fixture
def mock_endpoint():
    client = Mock()
    ctx = Mock()
    ctx.default_study_key = "DEF123"
    return SubjectsEndpoint(client, ctx, 200)


@patch("imednet.endpoints.subjects.Paginator")
@patch("imednet.endpoints.subjects.Subject")
@patch("imednet.endpoints.subjects.build_filter_string")
def test_list_with_study_key_and_filters(
    mock_build_filter, mock_subject, mock_paginator, mock_endpoint
):
    mock_build_filter.return_value = "foo=bar"
    mock_paginator.return_value = [{"id": 1}, {"id": 2}]
    mock_subject.from_json.side_effect = lambda x: x

    result = mock_endpoint.list(study_key="STUDY1", foo="bar")
    assert mock_build_filter.called
    assert mock_paginator.called
    assert result == [{"id": 1}, {"id": 2}]
    args, kwargs = mock_paginator.call_args
    assert kwargs["page_size"] == 200
    assert mock_subject.from_json.call_count == 2


@patch("imednet.endpoints.subjects.Paginator")
@patch("imednet.endpoints.subjects.Subject")
def test_list_with_only_study_key(mock_subject, mock_paginator, mock_endpoint):
    mock_paginator.return_value = [{"id": 1}]
    mock_subject.from_json.side_effect = lambda x: x

    result = mock_endpoint.list(study_key="STUDY2")
    assert result == [{"id": 1}]
    assert mock_subject.from_json.call_count == 1
    args, kwargs = mock_paginator.call_args
    assert kwargs["page_size"] == 200


@patch("imednet.endpoints.subjects.Paginator")
@patch("imednet.endpoints.subjects.Subject")
def test_list_uses_default_study_key(mock_subject, mock_paginator, mock_endpoint):
    mock_paginator.return_value = [{"id": 1}]
    mock_subject.from_json.side_effect = lambda x: x

    result = mock_endpoint.list()
    assert result == [{"id": 1}]
    assert mock_subject.from_json.call_count == 1
    args, kwargs = mock_paginator.call_args
    assert kwargs["page_size"] == 200


@patch("imednet.endpoints.subjects.Paginator")
@patch("imednet.endpoints.subjects.Subject")
def test_custom_page_size(mock_subject, mock_paginator, mock_endpoint):
    mock_paginator.return_value = []
    mock_subject.from_json.side_effect = lambda x: x

    mock_endpoint.list(page_size=30)
    args, kwargs = mock_paginator.call_args
    assert kwargs["page_size"] == 30


def test_list_raises_value_error_if_no_study_key():
    client = Mock()
    ctx = Mock()
    ctx.default_study_key = None
    endpoint = SubjectsEndpoint(client, ctx)
    with pytest.raises(TypeError):
        endpoint.list()


@patch("imednet.endpoints.subjects.Subject")
def test_get_returns_subject(mock_subject, mock_endpoint):
    mock_subject.from_json.return_value = {"id": "subj1"}
    mock_endpoint._client.get.return_value.json.return_value = {"data": [{"id": "subj1"}]}
    result = mock_endpoint.get("STUDY3", "subj1")
    assert result == {"id": "subj1"}
    mock_subject.from_json.assert_called_once_with({"id": "subj1"})


def test_get_raises_value_error_if_not_found(mock_endpoint):
    mock_endpoint._client.get.return_value.json.return_value = {"data": []}
    with pytest.raises(ValueError, match="Subject subj2 not found in study STUDY3"):
        mock_endpoint.get("STUDY3", "subj2")
