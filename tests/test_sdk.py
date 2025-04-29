from unittest.mock import MagicMock, patch

import pytest
from imednet.sdk import ImednetSDK, Workflows
from imednet.workflows.data_extraction import DataExtractionWorkflow
from imednet.workflows.query_management import QueryManagementWorkflow
from imednet.workflows.record_mapper import RecordMapper
from imednet.workflows.record_update import RecordUpdateWorkflow
from imednet.workflows.subject_data import SubjectDataWorkflow


@pytest.fixture
def mock_client():
    with patch("imednet.sdk.Client") as MockClient:
        client_instance = MockClient.return_value
        yield client_instance


@pytest.fixture
def mock_context():
    with patch("imednet.sdk.Context") as MockContext:
        context_instance = MockContext.return_value
        yield context_instance


@pytest.fixture
def sdk(mock_client, mock_context):
    with patch("imednet.sdk.Context", return_value=mock_context):
        return ImednetSDK(api_key="test_key", security_key="test_security")


class TestImednetSDK:
    def test_initialization(self):
        # Patch Client at the class level to capture constructor calls
        with patch("imednet.sdk.Client") as MockClient:
            sdk = ImednetSDK(
                api_key="test_api_key",
                security_key="test_security_key",
                base_url="https://test.example.com",
                timeout=45.0,
                retries=5,
                backoff_factor=2.0,
            )
            MockClient.assert_called_once_with(
                api_key="test_api_key",
                security_key="test_security_key",
                base_url="https://test.example.com",
                timeout=45.0,
                retries=5,
                backoff_factor=2.0,
            )

            # Check that all endpoints are initialized
            assert hasattr(sdk, "codings")
            assert hasattr(sdk, "forms")
            assert hasattr(sdk, "intervals")
            assert hasattr(sdk, "jobs")
            assert hasattr(sdk, "queries")
            assert hasattr(sdk, "record_revisions")
            assert hasattr(sdk, "records")
            assert hasattr(sdk, "sites")
            assert hasattr(sdk, "studies")
            assert hasattr(sdk, "subjects")
            assert hasattr(sdk, "users")
            assert hasattr(sdk, "variables")
            assert hasattr(sdk, "visits")

            # Check that workflows are initialized
            assert hasattr(sdk, "workflows")
            assert isinstance(sdk.workflows, Workflows)

    def test_context_manager(self, sdk, mock_client):
        # Test context manager protocol
        with sdk as sdk_instance:
            assert sdk_instance is sdk

        # Should call close on exit
        mock_client.close.assert_called_once()

    def test_close_method(self, sdk, mock_client):
        # Test that close method calls client's close method
        sdk.close()
        mock_client.close.assert_called_once()

    def test_set_default_study(self, sdk, mock_context):
        # Test setting default study
        study_key = "test_study_123"
        sdk.set_default_study(study_key)
        mock_context.set_default_study_key.assert_called_once_with(study_key)

    def test_clear_default_study(self, sdk, mock_context):
        # Test clearing default study
        sdk.clear_default_study()
        mock_context.clear_default_study_key.assert_called_once()


class TestWorkflows:
    def test_workflows_initialization(self):
        # Create a mock SDK instance
        mock_sdk = MagicMock()

        # Initialize workflows with the mock SDK
        workflows = Workflows(mock_sdk)

        # Verify all workflow attributes exist and were initialized with SDK
        assert hasattr(workflows, "data_extraction")
        assert hasattr(workflows, "query_management")
        assert hasattr(workflows, "record_mapper")
        assert hasattr(workflows, "record_update")
        assert hasattr(workflows, "subject_data")

        # Check that each workflow was initialized with the SDK instance

        assert isinstance(workflows.data_extraction, DataExtractionWorkflow)
        assert isinstance(workflows.query_management, QueryManagementWorkflow)
        assert isinstance(workflows.record_mapper, RecordMapper)
        assert isinstance(workflows.record_update, RecordUpdateWorkflow)
        assert isinstance(workflows.subject_data, SubjectDataWorkflow)
