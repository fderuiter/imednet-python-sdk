from unittest.mock import MagicMock, patch

from imednet.workflows.inventory_management import InventoryManagementWorkflow


def test_list_catalog_items_builds_filter_and_calls_sdk():
    sdk = MagicMock()
    sdk.records.list.return_value = []
    wf = InventoryManagementWorkflow(sdk)

    with patch(
        "imednet.workflows.inventory_management.build_filter_string", return_value="f"
    ) as bfs:
        result = wf.list_catalog_items("ST", deviceId=5)

    bfs.assert_called_once_with({"recordType": "CATALOG", "deviceId": 5})
    sdk.records.list.assert_called_once_with("ST", filter="f")
    assert result == []
