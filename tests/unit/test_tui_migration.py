import pytest
from datetime import datetime
from imednet.models.jobs import Job
from imednet.models.subjects import Subject
from imednet.form_designer.client import FormDesignerClient
from imednet.form_designer.models import Layout


def test_job_status_properties():
    """Verify logic migrated from TUI JobMonitor."""
    # Test Success cases
    j1 = Job(jobId="1", batchId="1", state="Completed")
    assert j1.is_terminal is True
    assert j1.is_successful is True
    assert j1.is_failed is False

    j2 = Job(jobId="2", batchId="2", state="Success")
    assert j2.is_successful is True

    # Test Pending cases
    j3 = Job(jobId="3", batchId="3", state="Processing")
    assert j3.is_terminal is False
    assert j3.is_successful is False
    assert j3.is_failed is False

    # Test Failure cases
    j4 = Job(jobId="4", batchId="4", state="Failed")
    assert j4.is_terminal is True
    assert j4.is_failed is True


def test_subject_filtering_logic():
    """Verify logic migrated from TUI SubjectTable."""
    from imednet.endpoints.subjects import SubjectsEndpoint
    from unittest.mock import Mock

    # Mock data
    s1 = Subject(studyKey="sk", subjectId=1, siteId=101, subjectKey="s1")
    s2 = Subject(studyKey="sk", subjectId=2, siteId=102, subjectKey="s2")
    s3 = Subject(studyKey="sk", subjectId=3, siteId=101, subjectKey="s3")  # Matches 101

    # Mock client and endpoint
    mock_client = Mock()
    mock_client.get.return_value.json.return_value = {
        "data": [
            s1.model_dump(by_alias=True),
            s2.model_dump(by_alias=True),
            s3.model_dump(by_alias=True),
        ],
        "pagination": {"totalPages": 1},
    }
    mock_ctx = Mock()
    mock_ctx.default_study_key = "sk"

    endpoint = SubjectsEndpoint(mock_client, mock_ctx)

    # Act: Filter by site 101
    filtered = endpoint.list_by_site("sk", 101)

    # Assert
    assert len(filtered) == 2
    assert all(s.site_id == 101 for s in filtered)
    assert filtered[0].subject_id == 1
    assert filtered[1].subject_id == 3


def test_form_designer_validation():
    """Verify validation logic migrated from TUI FormBuilderPane."""
    client = FormDesignerClient("http://test", "sess")
    layout = Layout(pages=[])

    # Test invalid form_id
    with pytest.raises(ValueError, match="Invalid form_id"):
        client.save_form("csrf", 0, 500, 1, layout)

    # Test empty CSRF
    with pytest.raises(ValueError, match="CSRF Key"):
        client.save_form("", 100, 500, 1, layout)
