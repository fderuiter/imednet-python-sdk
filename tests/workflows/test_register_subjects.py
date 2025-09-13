from unittest.mock import MagicMock

from imednet.api.models.jobs import Job
from imednet.api.models.records import RegisterSubjectRequest
from imednet.api.models.sites import Site
from imednet.api.models.subjects import Subject
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
