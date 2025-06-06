from unittest.mock import MagicMock, patch

import pytest
from imednet.models.subjects import Subject
from imednet.workflows.visit_tracking import VisitTrackingWorkflow


@pytest.fixture
def mock_sdk():
    return MagicMock()


def test_summary_by_subject(mock_sdk):
    subject1 = Subject(
        study_key="ST",
        subject_id=1,
        subject_oid="SO1",
        subject_key="SUBJ1",
        subject_status="",
        site_id=1,
        site_name="",
        deleted=False,
        enrollment_start_date="2024-01-01T00:00:00",
        date_created="2024-01-01T00:00:00",
        date_modified="2024-01-01T00:00:00",
        keywords=[],
    )
    subject2 = Subject(
        study_key="ST",
        subject_id=2,
        subject_oid="SO2",
        subject_key="SUBJ2",
        subject_status="",
        site_id=1,
        site_name="",
        deleted=False,
        enrollment_start_date="2024-01-01T00:00:00",
        date_created="2024-01-01T00:00:00",
        date_modified="2024-01-01T00:00:00",
        keywords=[],
    )
    mock_sdk.subjects.list.return_value = [subject1, subject2]

    with patch("imednet.workflows.visit_tracking.VisitCompletionWorkflow") as mock_vc_cls:
        vc_instance = MagicMock()
        vc_instance.get_subject_progress.side_effect = [
            {"Visit": {"F1": "COMPLETE"}},
            {"Visit": {"F1": "MISSING"}},
        ]
        mock_vc_cls.return_value = vc_instance

        workflow = VisitTrackingWorkflow(mock_sdk)
        result = workflow.summary_by_subject("STUDY1")

        expected = {
            "SUBJ1": {"Visit": {"F1": "COMPLETE"}},
            "SUBJ2": {"Visit": {"F1": "MISSING"}},
        }
        assert result == expected
        mock_sdk.subjects.list.assert_called_once_with("STUDY1")
        assert vc_instance.get_subject_progress.call_count == 2
