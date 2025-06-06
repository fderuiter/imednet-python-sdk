from unittest.mock import Mock, patch

import pytest
from imednet.veeva import MappingInterface, VeevaVaultClient


def _client() -> VeevaVaultClient:
    return VeevaVaultClient(
        vault="testvault",
        client_id="cid",
        client_secret="secret",
        username="user",
        password="pass",
    )


def test_authenticate():
    client = _client()
    with patch.object(client._client, "post") as mock_post:
        mock_resp = Mock()
        mock_resp.json.return_value = {"access_token": "token"}
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp
        client.authenticate()
        assert client._access_token == "token"
        mock_post.assert_called_once()


def test_headers_without_auth():
    client = _client()
    with pytest.raises(RuntimeError):
        client._headers()


def test_get_picklists():
    client = _client()
    client._access_token = "token"
    with patch.object(client._client, "get") as mock_get:
        mock_resp = Mock()
        mock_resp.json.return_value = {"data": [1]}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        result = client.get_picklists()
        assert result == [1]
        mock_get.assert_called_once()


def test_get_object_metadata():
    client = _client()
    client._access_token = "token"
    with patch.object(client._client, "get") as mock_get:
        mock_resp = Mock()
        mock_resp.json.return_value = {"data": {"fields": []}}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        result = client.get_object_metadata("obj")
        assert result == {"fields": []}
        mock_get.assert_called_once()


def test_upsert_object():
    client = _client()
    client._access_token = "token"
    with patch.object(client._client, "post") as mock_post:
        mock_resp = Mock()
        mock_resp.json.return_value = {"data": {"id": "1"}}
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp
        result = client.upsert_object("obj", {"field": "val"})
        assert result == {"id": "1"}
        mock_post.assert_called_once()


def test_mapping_interface():
    interface = MappingInterface(["a", "b"])
    options = interface.dropdown_options(["x", "y"])
    assert options == {"x": ["a", "b"], "y": ["a", "b"]}
    mapped = interface.apply_mapping({"x": 1, "z": 2}, {"x": "a"})
    assert mapped == {"a": 1, "z": 2}


def test_describe_object():
    client = _client()
    client._access_token = "token"
    with (
        patch.object(client, "get_object_metadata") as mock_meta,
        patch.object(client, "get_picklist_values") as mock_pick,
        patch.object(client._client, "get") as mock_get,
    ):
        mock_meta.return_value = {
            "fields": [
                {"name": "field1", "required": True},
                {"name": "pick", "type": "Picklist", "picklist": "pl"},
            ]
        }

        resp = Mock()
        resp.json.return_value = {"data": {"fields": [{"name": "extra", "required": True}]}}
        resp.raise_for_status.return_value = None
        mock_get.return_value = resp

        mock_pick.return_value = ["A", "B"]

        result = client.describe_object("obj", object_type="type")

        assert result == {
            "required_fields": ["extra", "field1"],
            "picklists": {"pick": ["A", "B"]},
        }
        mock_meta.assert_called_once_with("obj")
        mock_get.assert_called_once()
        mock_pick.assert_called_once_with("pl")
