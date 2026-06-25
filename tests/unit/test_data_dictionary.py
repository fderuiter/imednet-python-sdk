"""Unit tests for data dictionary."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

from imednet.validation import DataDictionary, DataDictionaryLoader

FIXTURES = Path(__file__).parent.parent / "fixtures" / "data_dictionary"


def _expected() -> DataDictionary:
    """Helper function to  expected."""
    return DataDictionaryLoader.from_directory(FIXTURES)


def test_from_directory() -> None:
    """Test that from directory."""
    dd = DataDictionaryLoader.from_directory(FIXTURES)
    assert isinstance(dd, DataDictionary)
    assert len(dd.forms) == 3
    assert dd.forms[0]["Form Key"] == "AE"


def test_from_zip() -> None:
    """Test that from zip."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        for name in DataDictionaryLoader.REQUIRED_FILES:
            zf.write(FIXTURES / name, arcname=name)
    buffer.seek(0)
    dd = DataDictionaryLoader.from_zip(buffer)
    expected = _expected()
    assert dd == expected
