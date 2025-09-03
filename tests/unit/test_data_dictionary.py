from __future__ import annotations

import io
import zipfile
from pathlib import Path

from imednet.validation import DataDictionary, DataDictionaryLoader

FIXTURES = Path(__file__).parent.parent


def _expected() -> DataDictionary:
    return DataDictionaryLoader.from_directory(FIXTURES)


def test_from_directory() -> None:
    dd = DataDictionaryLoader.from_directory(FIXTURES)
    assert isinstance(dd, DataDictionary)
    assert len(dd.forms) == 52


def test_from_zip() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        for name in DataDictionaryLoader.REQUIRED_FILES:
            zf.write(FIXTURES / name, arcname=name)
    buffer.seek(0)
    dd = DataDictionaryLoader.from_zip(buffer)
    assert isinstance(dd, DataDictionary)
    assert len(dd.forms) == 52
