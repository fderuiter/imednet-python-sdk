from unittest.mock import MagicMock, patch

import pytest
from imednet.veeva import VeevaVaultClient
from imednet.workflows.veeva_push import VeevaPushWorkflow


@pytest.fixture
def mock_sdk():
    sdk = MagicMock()
    sdk.records.list = MagicMock()
    return sdk


@pytest.fixture
def mock_client():
    client = MagicMock(spec=VeevaVaultClient)
    return client


def test_push_form_records_authenticate_called(mock_sdk, mock_client):
    mock_client._access_token = None
    mock_sdk.records.list.return_value = []
    wf = VeevaPushWorkflow(mock_sdk, mock_client)
    wf.push_form_records("STUDY", "FORM", "prod__c", {})
    mock_client.authenticate.assert_called_once()


def test_push_form_records_success(mock_sdk, mock_client):
    mock_client._access_token = "token"
    record = MagicMock()
    record.record_data = {"a": 1}
    mock_sdk.records.list.return_value = [record]
    mock_client.upsert_object.return_value = {"id": "1"}
    with patch(
        "imednet.workflows.veeva_push.validate_record_for_upsert", return_value={"a__v": 1}
    ) as mock_validate:
        wf = VeevaPushWorkflow(mock_sdk, mock_client)
        result = wf.push_form_records(
            "STUDY",
            "FORM",
            "prod__c",
            {"a": "a__v"},
        )
        mock_validate.assert_called_once()
        mock_client.upsert_object.assert_called_once_with("prod__c", {"a__v": 1})
        assert result == [{"id": "1"}]
