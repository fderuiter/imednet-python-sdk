from unittest.mock import MagicMock

from imednet.models.jobs import Job
from imednet.models.records import RegisterSubjectRequest
from imednet.testing import fake_data
from imednet.workflows.register_subjects import RegisterSubjectsWorkflow


def test_register_subjects_passes_records_correctly(schema) -> None:
    sdk = MagicMock()
    job = Job(batch_id="1", state="PROCESSING")
    sdk.records.create.return_value = job
    wf = RegisterSubjectsWorkflow(sdk)
    rec = fake_data.fake_record(schema)
    req = RegisterSubjectRequest(form_key=rec["formKey"], site_name="SITE", data=rec["recordData"])

    result = wf.register_subjects("STUDY", [req], email_notify="test@example.com")

    sdk.records.create.assert_called_once_with(
        study_key="STUDY",
        records_data=[req.model_dump(by_alias=True)],
        email_notify="test@example.com",
    )
    assert result == job
