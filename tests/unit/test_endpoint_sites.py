from unittest.mock import Mock, patch

import pytest
from imednet.endpoints.sites import SitesEndpoint


@pytest.fixture
def mock_endpoint():
    client = Mock()
    ctx = Mock()
    ctx.default_study_key = "DEF123"
    return SitesEndpoint(client, ctx)


@patch("imednet.endpoints.sites.Paginator")
@patch("imednet.endpoints.sites.Site")
@patch("imednet.endpoints.sites.build_filter_string")
def test_list_with_study_key_and_filters(
    mock_build_filter, mock_site, mock_paginator, mock_endpoint
):
    mock_build_filter.return_value = "foo=bar"
    mock_paginator.return_value = [{"id": 1}, {"id": 2}]
    mock_site.from_json.side_effect = lambda x: x

    result = mock_endpoint.list(study_key="STUDY1", foo="bar")
    assert mock_build_filter.called
    assert mock_paginator.called
    assert result == [{"id": 1}, {"id": 2}]
    assert mock_site.from_json.call_count == 2


@patch("imednet.endpoints.sites.Paginator")
@patch("imednet.endpoints.sites.Site")
def test_list_with_only_study_key(mock_site, mock_paginator, mock_endpoint):
    mock_paginator.return_value = [{"id": 1}]
    mock_site.from_json.side_effect = lambda x: x

    result = mock_endpoint.list(study_key="STUDY2")
    assert result == [{"id": 1}]
    assert mock_site.from_json.call_count == 1


@patch("imednet.endpoints.sites.Paginator")
@patch("imednet.endpoints.sites.Site")
def test_list_uses_default_study_key(mock_site, mock_paginator, mock_endpoint):
    mock_paginator.return_value = [{"id": 1}]
    mock_site.from_json.side_effect = lambda x: x

    result = mock_endpoint.list()
    assert result == [{"id": 1}]
    assert mock_site.from_json.call_count == 1


def test_list_raises_value_error_if_no_study_key():
    client = Mock()
    ctx = Mock()
    ctx.default_study_key = None
    endpoint = SitesEndpoint(client, ctx)
    with pytest.raises(KeyError):
        endpoint.list()


@patch("imednet.endpoints.sites.Site")
def test_get_returns_site(mock_site, mock_endpoint):
    mock_site.from_json.return_value = {"id": 123}
    mock_endpoint._client.get.return_value.json.return_value = {"data": [{"id": 123}]}
    result = mock_endpoint.get("STUDY3", 123)
    assert result == {"id": 123}
    mock_site.from_json.assert_called_once_with({"id": 123})


def test_get_raises_value_error_if_not_found(mock_endpoint):
    mock_endpoint._client.get.return_value.json.return_value = {"data": []}
    with pytest.raises(ValueError, match="Site 456 not found in study STUDY3"):
        mock_endpoint.get("STUDY3", 456)
