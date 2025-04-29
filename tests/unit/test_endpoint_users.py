from unittest.mock import Mock, patch

import pytest
from imednet.endpoints.users import UsersEndpoint


@pytest.fixture
def mock_endpoint():
    client = Mock()
    ctx = Mock()
    ctx.default_study_key = "DEF123"
    return UsersEndpoint(client, ctx)


@patch("imednet.endpoints.users.Paginator")
@patch("imednet.endpoints.users.User")
def test_list_with_study_key_and_include_inactive(mock_user, mock_paginator, mock_endpoint):
    mock_paginator.return_value = [{"id": 1}, {"id": 2}]
    mock_user.from_json.side_effect = lambda x: x

    result = mock_endpoint.list(study_key="STUDY1", include_inactive=True)
    assert mock_paginator.called
    assert result == [{"id": 1}, {"id": 2}]
    assert mock_user.from_json.call_count == 2
    args, kwargs = mock_paginator.call_args
    assert kwargs["params"]["includeInactive"] == "true"


@patch("imednet.endpoints.users.Paginator")
@patch("imednet.endpoints.users.User")
def test_list_uses_default_study_key_and_include_inactive_false(
    mock_user, mock_paginator, mock_endpoint
):
    mock_paginator.return_value = [{"id": 1}]
    mock_user.from_json.side_effect = lambda x: x

    result = mock_endpoint.list()
    assert result == [{"id": 1}]
    assert mock_user.from_json.call_count == 1
    args, kwargs = mock_paginator.call_args
    assert kwargs["params"]["includeInactive"] == "false"


def test_list_raises_value_error_if_no_study_key():
    client = Mock()
    ctx = Mock()
    ctx.default_study_key = None
    endpoint = UsersEndpoint(client, ctx)
    with pytest.raises(ValueError, match="Study key must be provided or set in the context"):
        endpoint.list()


@patch("imednet.endpoints.users.User")
def test_get_returns_user(mock_user, mock_endpoint):
    mock_user.from_json.return_value = {"id": "user1"}
    mock_endpoint._client.get.return_value.json.return_value = {"data": [{"id": "user1"}]}
    result = mock_endpoint.get("STUDY3", "user1")
    assert result == {"id": "user1"}
    mock_user.from_json.assert_called_once_with({"id": "user1"})


def test_get_raises_value_error_if_not_found(mock_endpoint):
    mock_endpoint._client.get.return_value.json.return_value = {"data": []}
    with pytest.raises(ValueError, match="User user2 not found in study STUDY3"):
        mock_endpoint.get("STUDY3", "user2")
