from __future__ import annotations

import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from imednet.cli import app
from imednet.validation import DataDictionaryLoader

runner = CliRunner()

FIXTURES = Path(__file__).parent.parent.parent / "fixtures" / "data_dictionary"


@pytest.fixture
def zip_file_path() -> Path:
    """Create a dummy zip file and return the path."""
    zip_path = Path("test_dd.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        for name in DataDictionaryLoader.REQUIRED_FILES:
            zf.write(FIXTURES / name, arcname=name)
    yield zip_path
    zip_path.unlink()


def test_load_data_dictionary_from_zip(zip_file_path: Path) -> None:
    """Test loading a data dictionary from a zip file."""
    result = runner.invoke(
        app, ["testing", "data-dictionary", "load", "--zip-file", str(zip_file_path)]
    )
    assert result.exit_code == 0
    assert "Loaded data dictionary." in result.stdout


def test_load_data_dictionary_from_files() -> None:
    """Test loading a data dictionary from individual files."""
    result = runner.invoke(
        app,
        [
            "testing",
            "data-dictionary",
            "load",
            "--business-logic-file",
            str(FIXTURES / "BUSINESS_LOGIC.csv"),
            "--choices-file",
            str(FIXTURES / "CHOICES.csv"),
            "--forms-file",
            str(FIXTURES / "FORMS.csv"),
            "--questions-file",
            str(FIXTURES / "QUESTIONS.csv"),
        ],
    )
    assert result.exit_code == 0
    assert "Loaded data dictionary." in result.stdout


def test_load_data_dictionary_missing_args() -> None:
    """Test that the command fails with missing arguments."""
    result = runner.invoke(app, ["testing", "data-dictionary", "load"])
    assert result.exit_code == 1
    assert "Error: You must provide either --zip-file or all four CSV file options." in result.stdout


def test_generate_records_cli(zip_file_path: Path) -> None:
    """Test the generate-records CLI command."""
    with patch("imednet.testing.data_dictionary.ImednetSDK") as mock_sdk_class, \
         patch("imednet.testing.data_dictionary.RecordGenerator") as mock_generator_class:
        mock_sdk_instance = mock_sdk_class.return_value
        mock_generator_instance = mock_generator_class.return_value
        mock_job = MagicMock()
        mock_generator_instance.generate_and_submit_form.return_value = mock_job

        result = runner.invoke(
            app,
            [
                "testing",
                "data-dictionary",
                "generate-records",
                "--form",
                "AE",
                "--study",
                "STUDY1",
                "--subject",
                "SUBJ1",
                "--zip-file",
                str(zip_file_path),
                "--wait",
            ],
        )

        assert result.exit_code == 0
        mock_sdk_class.assert_called_once()
        mock_generator_class.assert_called_once()
        mock_generator_instance.generate_and_submit_form.assert_called_once_with(
            form_key="AE",
            study_key="STUDY1",
            subject_identifier="SUBJ1",
            wait_for_completion=True,
        )
        assert "Record submission initiated." in result.stdout
