from unittest.mock import MagicMock, patch

import pytest
from imednet.models.records import Record
from imednet.models.study_structure import FormStructure, IntervalStructure, StudyStructure
from imednet.workflows.visit_completion import VisitCompletionWorkflow


@pytest.fixture
def mock_sdk():
    return MagicMock()


def test_get_subject_progress(mock_sdk):
    structure = StudyStructure(
        study_key="STUDY1",
        intervals=[
            IntervalStructure(
                interval_id=1,
                interval_name="Visit 1",
                interval_sequence=1,
                interval_description="",
                interval_group_name="",
                disabled=False,
                date_created="2024-01-01T00:00:00",
                date_modified="2024-01-01T00:00:00",
                forms=[
                    FormStructure(
                        form_id=10,
                        form_key="FORM1",
                        form_name="Form 1",
                        form_type="CRF",
                        revision=1,
                        disabled=False,
                        epro_form=False,
                        allow_copy=False,
                        date_created="2024-01-01T00:00:00",
                        date_modified="2024-01-01T00:00:00",
                        variables=[],
                    )
                ],
            )
        ],
    )
    record = Record(
        study_key="STUDY1",
        interval_id=1,
        form_id=10,
        form_key="FORM1",
        site_id=1,
        record_id=1,
        record_oid="R1",
        record_type="SCHEDULED",
        record_status="COMPLETE",
        deleted=False,
        date_created="2024-01-01T00:00:00",
        date_modified="2024-01-01T00:00:00",
        subject_id=1,
        subject_oid="S1",
        subject_key="SUBJ1",
        visit_id=1,
        parent_record_id=0,
        keywords=[],
        record_data={},
    )

    with patch("imednet.workflows.visit_completion.get_study_structure", return_value=structure):
        mock_sdk.records.list.return_value = [record]
        wf = VisitCompletionWorkflow(mock_sdk)
        result = wf.get_subject_progress("STUDY1", "SUBJ1")
        assert result == {"Visit 1": {"FORM1": "COMPLETE"}}
        mock_sdk.records.list.assert_called_once()
