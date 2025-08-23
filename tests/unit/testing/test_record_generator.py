from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from imednet.testing.record_generator import RecordGenerator
from imednet.validation import DataDictionary, DataDictionaryLoader
from tests.unit.test_data_dictionary import FIXTURES


@pytest.fixture
def data_dictionary() -> DataDictionary:
    """Return a DataDictionary instance loaded from fixtures."""
    return DataDictionaryLoader.from_directory(FIXTURES)


@pytest.fixture
def mock_sdk() -> MagicMock:
    """Return a mock ImednetSDK instance."""
    return MagicMock()


def test_record_generator_init(mock_sdk: MagicMock, data_dictionary: DataDictionary) -> None:
    """Test that the RecordGenerator initializes correctly."""
    generator = RecordGenerator(mock_sdk, data_dictionary)
    assert generator.sdk is mock_sdk
    assert generator.data_dictionary is data_dictionary
    assert "AE" in generator.forms
    assert "AE" in generator.questions
    assert ("AE", "AESEV") in generator.choices
    assert "AE" in generator.business_rules


def test_generate_form_data(mock_sdk: MagicMock, data_dictionary: DataDictionary) -> None:
    """Test that form data is generated correctly."""
    generator = RecordGenerator(mock_sdk, data_dictionary)
    form_data = generator.generate_form_data("AE")

    # This is a basic check. The logic is more thoroughly tested in
    # test_generate_form_data_with_logic.
    assert isinstance(form_data, dict)


def test_generate_and_submit_form(mock_sdk: MagicMock, data_dictionary: DataDictionary) -> None:
    """Test that the form submission workflow is called correctly."""
    generator = RecordGenerator(mock_sdk, data_dictionary)

    with patch("imednet.testing.record_generator.RecordUpdateWorkflow") as mock_workflow_class:
        mock_workflow_instance = mock_workflow_class.return_value
        mock_job = MagicMock()
        mock_workflow_instance.create_new_record.return_value = mock_job

        job = generator.generate_and_submit_form(
            form_key="AE",
            study_key="STUDY1",
            subject_identifier="SUBJ1",
            wait_for_completion=True,
        )

        mock_workflow_class.assert_called_once_with(mock_sdk)
        mock_workflow_instance.create_new_record.assert_called_once()
        args, kwargs = mock_workflow_instance.create_new_record.call_args
        assert kwargs["study_key"] == "STUDY1"
        assert kwargs["form_identifier"] == "AE"
        assert kwargs["subject_identifier"] == "SUBJ1"
        assert "data" in kwargs
        assert "AESTDAT" in kwargs["data"]
        assert kwargs["wait_for_completion"] is True
        assert job is mock_job


def test_apply_business_logic(
    mock_sdk: MagicMock, data_dictionary: DataDictionary
) -> None:
    """Test that the business logic is applied correctly."""
    generator = RecordGenerator(mock_sdk, data_dictionary)

    # Test case where the condition is met
    record_data = {"IRBDATCB": "1", "IRBDAT": "2025-01-01"}
    processed_data = generator._apply_business_logic("AE", record_data)
    assert "IRBDAT" not in processed_data

    # Test case where the condition is not met
    record_data = {"IRBDATCB": "0", "IRBDAT": "2025-01-01"}
    processed_data = generator._apply_business_logic("AE", record_data)
    assert "IRBDAT" in processed_data
