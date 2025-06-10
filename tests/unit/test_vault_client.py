from __future__ import annotations

import json
from pathlib import Path

import pytest
import responses
from imednet.vault_client import (
    API_VER,
    VaultAuthError,
    VaultClient,
    VaultField,
)


def load_fixture(name: str) -> dict:
    path = Path(__file__).resolve().parent.parent / "fixtures" / name
    return json.loads(path.read_text())


def test_list_objects_success() -> None:
    client = VaultClient("tok", "https://vault.example.com")
    url = f"https://vault.example.com/api/{API_VER}/metadata/vobjects"
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            url,
            json={"data": [{"name__v": "subject__c", "label__v": "Subject"}]},
            status=200,
        )
        objs = client.list_objects()

    assert [o.name for o in objs] == ["subject__c"]
    assert [o.label for o in objs] == ["Subject"]


def test_get_object_fields_success() -> None:
    fixture = load_fixture("vault_subject_fields.json")
    client = VaultClient("tok", "https://vault.example.com")
    url = f"https://vault.example.com/api/{API_VER}/metadata/vobjects/subject__c"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, json=fixture, status=200)
        fields = client.get_object_fields("subject__c")

    assert isinstance(fields[0], VaultField)
    assert fields[0].required is True
    assert fields[-1].picklist_values == ["Screening", "Enrolled", "Completed"]


def test_auth_error() -> None:
    client = VaultClient("tok", "https://vault.example.com")
    url = f"https://vault.example.com/api/{API_VER}/metadata/vobjects"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, status=401)
        with pytest.raises(VaultAuthError):
            client.list_objects()
