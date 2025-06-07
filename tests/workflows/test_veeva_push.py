from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from imednet.veeva.vault import AsyncVeevaVaultClient, VeevaVaultClient
from imednet.workflows.veeva_push import AsyncVeevaPushWorkflow, VeevaPushWorkflow


@pytest.fixture
def client() -> VeevaVaultClient:
    return MagicMock(spec=VeevaVaultClient)


@pytest.fixture
def async_client() -> AsyncVeevaVaultClient:
    client = MagicMock(spec=AsyncVeevaVaultClient)
    client.upload_attachment = AsyncMock()
    client.bulk_upsert_objects = AsyncMock()
    return client


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


def test_push_records_bulk(client):
    wf = VeevaPushWorkflow(client)
    records = [{"n": 1}, {"n": 2}]
    with patch(
        "imednet.workflows.veeva_push.validate_record_for_upsert",
        side_effect=lambda c, o, r, t: r,
    ) as validate:
        client.bulk_upsert_objects.return_value = [{"id": 1}, {"id": 2}]
        result = wf.push_records_bulk(
            "prod__c",
            records,
            id_param="ext",
            migration_mode=True,
            no_triggers=True,
        )
        assert result == [{"id": 1}, {"id": 2}]
        assert validate.call_count == 2
        client.bulk_upsert_objects.assert_called_once_with(
            "prod__c",
            records,
            id_param="ext",
            migration_mode=True,
            no_triggers=True,
        )


@pytest.mark.asyncio
async def test_async_push_records_bulk(async_client: AsyncVeevaVaultClient):
    wf = AsyncVeevaPushWorkflow(async_client)
    records = [{"n": 1}, {"n": 2}]
    async_client.bulk_upsert_objects.return_value = [{"id": 1}, {"id": 2}]
    with patch(
        "imednet.workflows.veeva_push.validate_record_for_upsert",
        side_effect=lambda c, o, r, t: r,
    ) as validate:
        result = await wf.push_records_bulk("prod__c", records, id_param="ext")
        assert result == [{"id": 1}, {"id": 2}]
        assert validate.call_count == 2
        async_client.bulk_upsert_objects.assert_awaited_once_with(
            "prod__c",
            [{"n": 1}, {"n": 2}],
            id_param="ext",
            migration_mode=False,
            no_triggers=False,
        )
