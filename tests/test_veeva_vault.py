from unittest.mock import Mock, patch

import pytest
from imednet.veeva import (
    MappingInterface,
    VeevaVaultClient,
    collect_required_fields_and_picklists,
    validate_record_for_upsert,
)


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


def _metadata():
    return {
        "fields": [
            {"name": "name__v", "required": True},
            {
                "name": "status__v",
                "required": True,
                "picklist": {
                    "values": [{"name": "New"}, {"name": "Closed"}],
                    "defaultValue": "New",
                },
            },
            {
                "name": "category__v",
                "picklist": {"values": [{"name": "A"}, {"name": "B"}]},
            },
        ]
    }


def test_validate_record_for_upsert_success():
    client = _client()
    with patch.object(client, "get_object_metadata", return_value=_metadata()):
        record = {"name__v": "test", "status__v": "Closed"}
        result = validate_record_for_upsert(client, "prod__c", record)
        assert result == record


def test_validate_record_for_upsert_missing_required():
    client = _client()
    with patch.object(client, "get_object_metadata", return_value=_metadata()):
        with pytest.raises(ValueError):
            validate_record_for_upsert(client, "prod__c", {"status__v": "New"})


def test_validate_record_for_upsert_invalid_picklist():
    client = _client()
    with patch.object(client, "get_object_metadata", return_value=_metadata()):
        with pytest.raises(ValueError):
            validate_record_for_upsert(client, "prod__c", {"name__v": "test", "status__v": "Bad"})


def test_validate_record_for_upsert_autofill_default():
    client = _client()
    with patch.object(client, "get_object_metadata", return_value=_metadata()):
        record = {"name__v": "test"}
        result = validate_record_for_upsert(client, "prod__c", record)
        assert result["status__v"] == "New"


def _metadata_v2():
    return {
        "fields": [
            {"name": "name__v", "required": True, "type": "String"},
            {"name": "category__v", "type": "Picklist", "picklist": "cat_pl"},
        ]
    }


def _object_type_details():
    return {
        "type_fields": [
            {"name": "status__v", "required": True, "type": "Picklist", "picklist": "status_pl"}
        ]
    }


def test_collect_required_fields_and_picklists_without_object_type():
    client = _client()
    with (
        patch.object(client, "get_object_metadata", return_value=_metadata_v2()) as meta,
        patch.object(client, "get_object_type_details") as obj_type,
        patch.object(
            client, "get_picklist_values", return_value=[{"name": "A"}, {"name": "B"}]
        ) as pick,
    ):
        result = collect_required_fields_and_picklists(client, "prod__c")
        assert result == {"required_fields": ["name__v"], "picklists": {"category__v": ["A", "B"]}}
        meta.assert_called_once_with("prod__c")
        obj_type.assert_not_called()
        pick.assert_called_once_with("cat_pl")


def test_collect_required_fields_and_picklists_with_object_type():
    client = _client()
    with (
        patch.object(client, "get_object_metadata", return_value=_metadata_v2()) as meta,
        patch.object(
            client, "get_object_type_details", return_value=_object_type_details()
        ) as obj_type,
        patch.object(client, "get_picklist_values") as pick,
    ):
        pick.side_effect = [[{"name": "A"}, {"name": "B"}], [{"name": "X"}, {"name": "Y"}]]
        result = collect_required_fields_and_picklists(client, "prod__c", "special")
        assert result == {
            "required_fields": ["name__v", "status__v"],
            "picklists": {"category__v": ["A", "B"], "status__v": ["X", "Y"]},
        }
        meta.assert_called_once_with("prod__c")
        obj_type.assert_called_once_with("prod__c", "special")
        assert pick.call_args_list[0][0][0] == "cat_pl"
        assert pick.call_args_list[1][0][0] == "status_pl"


def test_get_picklist_values():
    client = _client()
    client._access_token = "token"
    with patch.object(client._client, "get") as mock_get:
        mock_resp = Mock()
        mock_resp.json.return_value = {
            "picklistValues": [
                {"name": "A"},
                {"name": "B"},
            ]
        }
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        result = client.get_picklist_values("my_pl")
        assert result == [{"name": "A"}, {"name": "B"}]
        mock_get.assert_called_once()


def test_get_object_field_metadata():
    client = _client()
    client._access_token = "token"
    with patch.object(client._client, "get") as mock_get:
        mock_resp = Mock()
        mock_resp.json.return_value = {"field": {"name": "status__v"}}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        result = client.get_object_field_metadata("obj", "status__v")
        assert result == {"name": "status__v"}
        mock_get.assert_called_once()
