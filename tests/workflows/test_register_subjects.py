from unittest.mock import MagicMock

import pytest

from imednet.models.jobs import Job
from imednet.models.records import RecordData, RegisterSubjectRequest
from imednet.models.sites import Site
from imednet.testing import fake_data
from imednet_workflows.register_subjects import RegisterSubjectsWorkflow


def test_register_subjects_passes_records_correctly(schema) -> None:
    sdk = MagicMock()
    job = Job(jobId="1", batchId="1", state="PROCESSING")
    sdk.records.create.return_value = job
    sdk.sites.list.return_value = [
        Site(studyKey="S", siteId=1, siteName="SITE", siteEnrollmentStatus="Active")
    ]
    wf = RegisterSubjectsWorkflow(sdk)
    rec = fake_data.fake_record(schema)
    req = RegisterSubjectRequest(
        formKey=rec["formKey"], siteName="SITE", data=RecordData(rec["recordData"])
    )

    result = wf.register_subjects("STUDY", [req], email_notify="test@example.com")

    sdk.sites.list.assert_called_once_with(study_key="STUDY")
    sdk.subjects.get.assert_not_called()
    sdk.records.create.assert_called_once_with(
        study_key="STUDY",
        records_data=[req.model_dump(by_alias=True)],
        email_notify="test@example.com",
    )
    assert result == job


def test_register_subjects_validation_errors() -> None:
    sdk = MagicMock()
    sdk.sites.list.return_value = [
        Site(studyKey="S", siteId=1, siteName="VALID_SITE", siteEnrollmentStatus="Active")
    ]
    wf = RegisterSubjectsWorkflow(sdk)

    subjects = [
        RegisterSubjectRequest(formKey="F1", siteName=""),
        RegisterSubjectRequest(formKey="F2", siteName="INVALID_SITE"),
    ]

    with pytest.raises(ValueError) as excinfo:
        wf.register_subjects("STUDY", subjects)

    error_msg = str(excinfo.value)
    assert "Index 0: siteName is required" in error_msg
    assert "Index 1: site 'INVALID_SITE' not found" in error_msg

    sdk.records.create.assert_not_called()
