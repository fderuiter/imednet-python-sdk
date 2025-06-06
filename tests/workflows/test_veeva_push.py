from unittest.mock import MagicMock, patch

import pytest
from imednet.veeva.vault import VeevaVaultClient
from imednet.workflows.veeva_push import VeevaPushWorkflow


@pytest.fixture
def client() -> VeevaVaultClient:
    return MagicMock(spec=VeevaVaultClient)


def test_push_record_validates_and_upserts(client):
    wf = VeevaPushWorkflow(client)
    record = {"name__v": "test"}
    with patch(
        "imednet.workflows.veeva_push.validate_record_for_upsert",
        return_value=record,
    ) as validate:
        client.upsert_object.return_value = {"id": "1"}
        result = wf.push_record("prod__c", record, object_type="special")
        validate.assert_called_once_with(client, "prod__c", record, "special")
        client.upsert_object.assert_called_once_with("prod__c", record)
        assert result == {"id": "1"}


def test_push_records_iterates(client):
    wf = VeevaPushWorkflow(client)
    records = [{"n": 1}, {"n": 2}]
    with patch(
        "imednet.workflows.veeva_push.validate_record_for_upsert",
        side_effect=lambda c, o, r, t: r,
    ) as validate:
        client.upsert_object.side_effect = [{"id": 1}, {"id": 2}]
        result = wf.push_records("prod__c", records)
        assert result == [{"id": 1}, {"id": 2}]
        assert validate.call_count == 2
        assert client.upsert_object.call_count == 2
