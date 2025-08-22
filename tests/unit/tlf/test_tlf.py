import pandas as pd
import pytest
from typer.testing import CliRunner
from unittest.mock import MagicMock

import imednet.cli as cli
from imednet.models.records import Record
from imednet.tlf.definitions import AdverseEventsListing

runner = CliRunner()


@pytest.fixture(autouse=True)
def env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set required environment variables for each test to bypass config errors."""
    monkeypatch.setenv("IMEDNET_API_KEY", "key")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "secret")


@pytest.fixture
def sdk(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Provide a mocked SDK instance and patch get_sdk."""
    mock_sdk = MagicMock()
    monkeypatch.setattr(cli, "get_sdk", MagicMock(return_value=mock_sdk))
    return mock_sdk


def test_adverse_events_listing_generate():
    """Test the generate method of the AdverseEventsListing class."""
    # This test does not use the CLI or the sdk fixture.
    # It tests the class logic in isolation.
    sdk_mock = MagicMock()
    fake_record_data = [
        Record(record_id=101, record_data={"SUBJECT_ID": "SUBJ-001", "AETERM": "Headache", "AESEV": "MILD"}),
        Record(record_id=102, record_data={"SUBJECT_ID": "SUBJ-002", "AETERM": "Nausea", "AESEV": "MODERATE"}),
    ]
    sdk_mock.records.list.return_value = fake_record_data
    definition = AdverseEventsListing()

    df = definition.generate(sdk_mock, "TEST_STUDY")

    assert not df.empty
    assert len(df) == 2
    sdk_mock.records.list.assert_called_once_with("TEST_STUDY", form_key="AE")


def test_cli_generate_success_stdout(sdk: MagicMock):
    """Test the 'tlf generate' command with stdout."""
    # 1. Arrange
    fake_record_data = [
        Record(record_id=101, record_data={"SUBJECT_ID": "001", "AETERM": "Fever"})
    ]
    sdk.records.list.return_value = fake_record_data

    # 2. Act
    result = runner.invoke(cli.app, ["tlf", "generate", "adverse_events", "FAKESTUDY"])

    # 3. Assert
    assert result.exit_code == 0, result.stdout
    assert "Generating TLF" in result.stdout
    assert "Fever" in result.stdout
    assert "Done" in result.stdout
    sdk.records.list.assert_called_once_with("FAKESTUDY", form_key="AE")


def test_cli_generate_success_file_output(sdk: MagicMock, tmp_path):
    """Test the 'tlf generate' command with file output."""
    # 1. Arrange
    output_file = tmp_path / "ae.csv"
    fake_record_data = [
        Record(record_id=101, record_data={"SUBJECT_ID": "001", "AETERM": "Fever"})
    ]
    sdk.records.list.return_value = fake_record_data

    # 2. Act
    result = runner.invoke(cli.app, ["tlf", "generate", "adverse_events", "FAKESTUDY", "--out", str(output_file)])

    # 3. Assert
    assert result.exit_code == 0, result.stdout
    assert "Output successfully saved to" in result.stdout
    assert str(output_file) in result.stdout
    assert output_file.exists()
    saved_df = pd.read_csv(output_file)
    assert saved_df.iloc[0]["AETERM"] == "Fever"


def test_cli_generate_unknown_tlf(sdk: MagicMock):
    """Test the 'tlf generate' command with an unknown TLF name."""
    result = runner.invoke(cli.app, ["tlf", "generate", "non_existent_tlf", "FAKESTUDY"])
    assert result.exit_code == 1
    assert "Error: Unknown TLF" in result.stdout
