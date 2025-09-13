from unittest.mock import MagicMock

import pytest

from imednet.api.core.exceptions import ApiError
from imednet.api.models.error import ApiErrorDetail
from imednet.api.models.jobs import Job
from imednet.api.models.records import RegisterSubjectRequest
from imednet.api.models.sites import Site
from imednet.api.models.subjects import Subject
from imednet.workflows.register_subjects import RegisterSubjectsWorkflow


def test_register_subjects_passes_records_correctly() -> None:
    sdk = MagicMock()
    job = Job(batch_id="1", state="PROCESSING")
    sdk.records.create.return_value = job
    sdk.sites.list.return_value = [Site(site_name="SITE")]
    sdk.subjects.get.return_value = Subject(subject_key="SUBJ", site_name="SITE")
    wf = RegisterSubjectsWorkflow(sdk)
    req = RegisterSubjectRequest(form_key="F", site_name="SITE", subject_key="SUBJ")

    result = wf.register_subjects("STUDY", [req], email_notify="test@example.com")

    sdk.sites.list.assert_called_once_with(study_key="STUDY")
    sdk.subjects.get.assert_called_once_with("STUDY", "SUBJ")
    sdk.records.create.assert_called_once_with(
        study_key="STUDY",
        records_data=[req.model_dump(by_alias=True)],
        email_notify="test@example.com",
    )
    assert result == job


def test_register_subjects_missing_site() -> None:
    sdk = MagicMock()
    sdk.sites.list.return_value = []
    wf = RegisterSubjectsWorkflow(sdk)
    req = RegisterSubjectRequest(form_key="F", site_name="SITE", subject_key="SUBJ")

    with pytest.raises(ValueError, match="site 'SITE' not found"):
        wf.register_subjects("STUDY", [req])


def test_register_subjects_missing_subject() -> None:
    sdk = MagicMock()
    sdk.sites.list.return_value = [Site(site_name="SITE")]
    sdk.subjects.get.side_effect = ValueError("not found")
    wf = RegisterSubjectsWorkflow(sdk)
    req = RegisterSubjectRequest(form_key="F", site_name="SITE", subject_key="SUBJ")

    with pytest.raises(ValueError, match="subject with subjectKey SUBJ not found"):
        wf.register_subjects("STUDY", [req])


def test_register_subjects_missing_subject_api_error() -> None:
    sdk = MagicMock()
    sdk.sites.list.return_value = [Site(site_name="SITE")]
    sdk.subjects.get.side_effect = ApiError(ApiErrorDetail(detail="oops"))
    wf = RegisterSubjectsWorkflow(sdk)
    req = RegisterSubjectRequest(form_key="F", site_name="SITE", subject_key="SUBJ")

    with pytest.raises(ValueError, match="subject with subjectKey SUBJ not found"):
        wf.register_subjects("STUDY", [req])


def test_register_subjects_unexpected_error_propagates() -> None:
    sdk = MagicMock()
    sdk.sites.list.return_value = [Site(site_name="SITE")]
    sdk.subjects.get.side_effect = RuntimeError("boom")
    wf = RegisterSubjectsWorkflow(sdk)
    req = RegisterSubjectRequest(form_key="F", site_name="SITE", subject_key="SUBJ")

    with pytest.raises(RuntimeError, match="boom"):
        wf.register_subjects("STUDY", [req])
