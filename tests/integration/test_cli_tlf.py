from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
import pandas as pd
from imednet.cli import app
from imednet.models import Subject
from imednet.endpoints import SubjectsEndpoint

runner = CliRunner()


@patch("imednet.cli.get_sdk")
def test_tlf_subject_listing_to_console(mock_get_sdk):
    # Arrange
    mock_sdk_instance = MagicMock()
    mock_sdk_instance.subjects = MagicMock(spec=SubjectsEndpoint)
    mock_get_sdk.return_value = mock_sdk_instance
    subjects_data = [
        Subject(
            subject_key="001",
            subject_status="Enrolled",
            site_name="Site A",
            enrollment_start_date="2023-01-01",
        )
    ]
    mock_sdk_instance.subjects.list.return_value = subjects_data

    # Act
    result = runner.invoke(app, ["tlf", "listing", "subject", "test_study"])

    # Assert
    assert result.exit_code == 0
    assert "001" in result.stdout
    assert "Enrolled" in result.stdout
    assert "Site A" in result.stdout


@patch("imednet.cli.get_sdk")
@patch("pandas.DataFrame.to_csv")
def test_tlf_subject_listing_to_file(mock_to_csv, mock_get_sdk):
    # Arrange
    mock_sdk_instance = MagicMock()
    mock_sdk_instance.subjects = MagicMock(spec=SubjectsEndpoint)
    mock_get_sdk.return_value = mock_sdk_instance
    subjects_data = [
        Subject(
            subject_key="001",
            subject_status="Enrolled",
            site_name="Site A",
            enrollment_start_date="2023-01-01",
        )
    ]
    mock_sdk_instance.subjects.list.return_value = subjects_data

    with runner.isolated_filesystem():
        # Act
        result = runner.invoke(
            app, ["tlf", "listing", "subject", "test_study", "--output-file", "subjects.csv"]
        )

        # Assert
        assert result.exit_code == 0
        assert "Report saved to subjects.csv" in result.stdout
        mock_to_csv.assert_called_once_with("subjects.csv", index=False)
