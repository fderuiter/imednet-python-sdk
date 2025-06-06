from unittest.mock import MagicMock

from imednet.models.record_revisions import RecordRevision
from imednet.workflows.audit_aggregation import AuditAggregationWorkflow


def test_summary_by_user_counts_revisions():
    mock_sdk = MagicMock()
    revisions = [
        RecordRevision(user="alice"),
        RecordRevision(user="bob"),
        RecordRevision(user="alice"),
    ]
    mock_sdk.record_revisions.list.return_value = revisions

    wf = AuditAggregationWorkflow(mock_sdk)
    result = wf.summary_by_user("STUDY1", start_date="2024-01-01", end_date="2024-01-31", site_id=1)

    mock_sdk.record_revisions.list.assert_called_once_with(
        "STUDY1",
        page_size=None,
        filter="site_id==1",
        start_date="2024-01-01",
        end_date="2024-01-31",
    )
    assert result == {"alice": 2, "bob": 1}


def test_summary_by_user_empty_result():
    mock_sdk = MagicMock()
    mock_sdk.record_revisions.list.return_value = []

    wf = AuditAggregationWorkflow(mock_sdk)
    result = wf.summary_by_user("STUDY1")

    mock_sdk.record_revisions.list.assert_called_once_with(
        "STUDY1",
        page_size=None,
        filter=None,
        start_date=None,
        end_date=None,
    )
    assert result == {}
