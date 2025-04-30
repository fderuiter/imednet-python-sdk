from unittest.mock import MagicMock

import pytest
from imednet.models.records import RegisterSubjectRequest
from imednet.workflows.register_subjects import RegisterSubjectsWorkflow

"""
Unit tests for the RegisterSubjectsWorkflow class.
"""


class TestRegisterSubjectsWorkflow:
    """Test suite for the RegisterSubjectsWorkflow class."""

    @pytest.fixture
    def mock_sdk(self):
        """Creates a mock SDK with records API."""
        mock = MagicMock()
        mock.records = MagicMock()
        mock.records.create = MagicMock()
        return mock

    @pytest.fixture
    def workflow(self, mock_sdk):
        """Creates a RegisterSubjectsWorkflow instance with mock SDK."""
        return RegisterSubjectsWorkflow(mock_sdk)

    @pytest.fixture
    def sample_subjects(self):
        """Creates sample RegisterSubjectRequest objects."""
        return [
            RegisterSubjectRequest(
                subject_key="SUBJ001", attributes={"firstName": "John", "lastName": "Doe"}
            ),
            RegisterSubjectRequest(
                subject_key="SUBJ002", attributes={"firstName": "Jane", "lastName": "Smith"}
            ),
        ]

    def test_init(self, mock_sdk):
        """Test that the workflow initializes with an SDK."""
        workflow = RegisterSubjectsWorkflow(mock_sdk)
        assert workflow._sdk == mock_sdk

    def test_register_subjects(self, workflow, mock_sdk, sample_subjects):
        """Test that register_subjects calls the SDK's records.create with correct parameters."""
        # Setup
        study_key = "STUDY123"
        email_notify = "test@example.com"
        expected_response = {"job_id": "job-123"}
        mock_sdk.records.create.return_value = expected_response

        # Execute
        response = workflow.register_subjects(
            study_key=study_key, subjects=sample_subjects, email_notify=email_notify
        )

        # Verify
        mock_sdk.records.create.assert_called_once()
        call_args = mock_sdk.records.create.call_args[1]
        assert call_args["study_key"] == study_key
        assert call_args["email_notify"] == email_notify
        assert len(call_args["records_data"]) == 2
        assert response == expected_response

    def test_register_subjects_without_email(self, workflow, mock_sdk, sample_subjects):
        """Test register_subjects without email notification."""
        # Setup
        study_key = "STUDY123"
        expected_response = {"job_id": "job-123"}
        mock_sdk.records.create.return_value = expected_response

        # Execute
        response = workflow.register_subjects(study_key=study_key, subjects=sample_subjects)

        # Verify
        mock_sdk.records.create.assert_called_once()
        call_args = mock_sdk.records.create.call_args[1]
        assert call_args["study_key"] == study_key
        assert call_args["email_notify"] is None
        assert response == expected_response

    def test_model_dump_called(self, workflow, mock_sdk):
        """Test that model_dump is called on each subject."""
        # Setup
        study_key = "STUDY123"
        mock_subject = MagicMock(spec=RegisterSubjectRequest)
        mock_subject.model_dump.return_value = {"subject_key": "SUBJ001"}

        # Execute
        workflow.register_subjects(study_key=study_key, subjects=[mock_subject])

        # Verify
        mock_subject.model_dump.assert_called_once_with(by_alias=True)
