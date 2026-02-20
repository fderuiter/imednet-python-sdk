import warnings
from unittest.mock import MagicMock

import pandas as pd
import pytest

import imednet.integrations.export as export_mod


@pytest.fixture
def mock_record_mapper(monkeypatch):
    """Fixture to mock RecordMapper with a configurable DataFrame."""
    mapper_inst = MagicMock()

    def _setup(df: pd.DataFrame):
        mapper_inst.dataframe.return_value = df
        monkeypatch.setattr(export_mod, "RecordMapper", MagicMock(return_value=mapper_inst))
        return mapper_inst

    return _setup


def test_export_to_csv_sanitization(tmp_path, mock_record_mapper):
    """Test that CSV export sanitizes formulas and raises no warnings."""
    df = pd.DataFrame({"safe": ["hello"], "unsafe": ["=cmd"]})
    mock_record_mapper(df)

    sdk = MagicMock()
    path = tmp_path / "out.csv"

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")  # Catch all warnings
        export_mod.export_to_csv(sdk, "STUDY", str(path))

        # Ensure no Pandas4Warning or other warnings related to sanitization
        relevant_warnings = [
            warning
            for warning in w
            if "Pandas4Warning" in str(warning.category.__name__)
            or "select_dtypes" in str(warning.message)
        ]
        assert (
            not relevant_warnings
        ), f"Caught unexpected warnings: {[str(warn.message) for warn in relevant_warnings]}"

    content = path.read_text()
    # Check that unsafe content is prefixed with a single quote
    assert "'=cmd" in content
    # Check that safe content is untouched (though to_csv might quote/escape, expected 'hello')
    assert "hello" in content


def test_export_to_excel_sanitization(tmp_path, mock_record_mapper, monkeypatch):
    """Test that Excel export sanitizes formulas."""
    df = pd.DataFrame({"safe": ["hello"], "unsafe": ["=cmd"], "num": [123]})
    mock_record_mapper(df)

    sdk = MagicMock()
    path = tmp_path / "out.xlsx"

    # We need to inspect the DataFrame passed to to_excel, because reading xlsx requires openpyxl
    # and might be complex to verify directly in test environment without full setup.
    # Instead, we patch pd.DataFrame.to_excel to verify the dataframe state just before export.

    captured_df = None
    original_to_excel = pd.DataFrame.to_excel

    def mock_to_excel(self, excel_writer, index=False, **kwargs):
        nonlocal captured_df
        captured_df = self.copy()
        # Call original to generate file if needed, but we can skip file generation for speed/dependency
        # Just creating an empty file to satisfy existence checks if any
        # However, export_mod doesn't check existence after.
        # But we need to ensure the method signature matches.
        pass

    monkeypatch.setattr(pd.DataFrame, "to_excel", mock_to_excel)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        export_mod.export_to_excel(sdk, "STUDY", str(path))

        relevant_warnings = [
            warning
            for warning in w
            if "Pandas4Warning" in str(warning.category.__name__)
            or "select_dtypes" in str(warning.message)
        ]
        assert (
            not relevant_warnings
        ), f"Caught unexpected warnings: {[str(warn.message) for warn in relevant_warnings]}"

    assert captured_df is not None
    assert captured_df["unsafe"].iloc[0] == "'=cmd"
    assert captured_df["safe"].iloc[0] == "hello"
    assert captured_df["num"].iloc[0] == 123


def test_sanitization_does_not_affect_non_strings(tmp_path, mock_record_mapper):
    """Test that sanitization ignores non-string columns."""
    df = pd.DataFrame(
        {
            "int_col": [1, 2, 3],
            "float_col": [1.1, 2.2, 3.3],
            "bool_col": [True, False, True],
            "str_col": ["=danger", "safe", "+formula"],
        }
    )
    mock_record_mapper(df)
    sdk = MagicMock()
    path = tmp_path / "out.csv"

    export_mod.export_to_csv(sdk, "STUDY", str(path))

    content = path.read_text()

    # Check sanitization occurred
    assert "'=danger" in content
    assert "'+formula" in content

    # Check numeric values are preserved (as strings in CSV)
    assert "1" in content
    assert "1.1" in content
    assert "True" in content

    # Ensure they were not somehow quoted with single quote like sanitization does
    assert "'1" not in content
    assert "'1.1" not in content
    assert "'True" not in content
