from unittest.mock import MagicMock

import pytest

from imednet.errors import ApiError
from imednet.models.jobs import Job
from imednet.models.records import RegisterSubjectRequest
from imednet.models.sites import Site
from imednet.models.subjects import Subject
from imednet.testing import fake_data
from imednet.workflows.register_subjects import RegisterSubjectsWorkflow


def test_register_subjects_passes_records_correctly(schema) -> None:
    sdk = MagicMock()
    job = Job(batch_id="1", state="PROCESSING")
    sdk.records.create.return_value = job
    sdk.sites.list.return_value = [Site(site_name="SITE")]
    sdk.subjects.get.return_value = Subject(subject_key="SUBJ", site_name="SITE")
    wf = RegisterSubjectsWorkflow(sdk)
    rec = fake_data.fake_record(schema)
    req = RegisterSubjectRequest(
        form_key=rec["formKey"], site_name="SITE", subject_key="SUBJ", data=rec["recordData"]
    )

    result = wf.register_subjects("STUDY", [req], email_notify="test@example.com")

    sdk.sites.list.assert_called_once_with(study_key="STUDY")
    sdk.subjects.get.assert_called_once_with("STUDY", "SUBJ")
    sdk.records.create.assert_called_once_with(
        study_key="STUDY",
        records_data=[req.model_dump(by_alias=True)],
        email_notify="test@example.com",
    )
    assert result == job


def test_register_subjects_validation_errors() -> None:
    sdk = MagicMock()
    sdk.sites.list.return_value = [Site(site_name="VALID_SITE")]

    # Mock subject fetch to succeed for "EXISTING_SUBJ" and raise ApiError for others
    def mock_subject_get(study_key, subject_key):
        if subject_key == "EXISTING_SUBJ":
            return Subject(subject_key="EXISTING_SUBJ", site_name="VALID_SITE")
        raise ApiError("Not found")

    sdk.subjects.get.side_effect = mock_subject_get

    wf = RegisterSubjectsWorkflow(sdk)

    subjects = [
        RegisterSubjectRequest(form_key="F1", site_name="", subject_key="SUBJ1", data={}),
        RegisterSubjectRequest(
            form_key="F2", site_name="INVALID_SITE", subject_key="SUBJ2", data={}
        ),
        RegisterSubjectRequest(form_key="F3", site_name="VALID_SITE", subject_key="", data={}),
        RegisterSubjectRequest(
            form_key="F4", site_name="VALID_SITE", subject_key="NEW_SUBJ", data={}
        ),
    ]

    with pytest.raises(ValueError) as excinfo:
        wf.register_subjects("STUDY", subjects)

    error_msg = str(excinfo.value)
    assert "Index 0: siteName is required" in error_msg
    assert "Index 1: site 'INVALID_SITE' not found" in error_msg
    assert "Index 2: subjectKey is required" in error_msg
    assert "Index 3: subject with subjectKey NEW_SUBJ not found" in error_msg

    sdk.records.create.assert_not_called()
