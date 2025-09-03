from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Iterator

import pytest
from typer.testing import CliRunner

from imednet.cli import app
from imednet.validation import DataDictionaryLoader

runner = CliRunner()

FIXTURES = Path(__file__).parent.parent.parent


@pytest.fixture
def zip_file_path() -> Iterator[Path]:
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


# def test_load_data_dictionary_from_files() -> None:
#     """Test loading a data dictionary from individual files."""
#     result = runner.invoke(
#         app,
#         [
#             "testing",
#             "data-dictionary",
#             "load",
#             "--business-logic-file",
#             str(FIXTURES / "BUSINESS_LOGIC.csv"),
#             "--choices-file",
#             str(FIXTURES / "CHOICES.csv"),
#             "--forms-file",
#             str(FIXTURES / "FORMS.csv"),
#             "--questions-file",
#             str(FIXTURES / "QUESTIONS.csv"),
#         ],
#     )
#     assert result.exit_code == 0
#     assert "Loaded data dictionary." in result.stdout


def test_load_data_dictionary_missing_args() -> None:
    """Test that the command fails with missing arguments."""
    result = runner.invoke(app, ["testing", "data-dictionary", "load"])
    assert result.exit_code == 1
    assert (
        "Error: You must provide either --zip-file or all four CSV file options."
        in result.stdout
    )
