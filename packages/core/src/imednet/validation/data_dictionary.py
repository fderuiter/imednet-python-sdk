from __future__ import annotations

import csv
import io
import zipfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterator, TextIO


@dataclass
class DataDictionary:
    """Container for data dictionary CSV content."""

    business_logic: list[dict[str, str]]
    choices: list[dict[str, str]]
    forms: list[dict[str, str]]
    questions: list[dict[str, str]]


class DataDictionaryLoader:
    """Load data dictionary files from various sources."""

    REQUIRED_FILES = {
        "BUSINESS_LOGIC.csv": "business_logic",
        "CHOICES.csv": "choices",
        "FORMS.csv": "forms",
        "QUESTIONS.csv": "questions",
    }

    @staticmethod
    @contextmanager
    def _open_text(source: Path | TextIO) -> Iterator[TextIO]:
        if isinstance(source, (str, Path)):
            with open(source, encoding="utf-8", newline="") as f:
                yield f
        else:
            yield source

    @classmethod
    def _load_csv(cls, source: Path | TextIO) -> list[dict[str, str]]:
        with cls._open_text(source) as f:
            reader = csv.DictReader(f)
            return list(reader)

    @classmethod
    def from_files(
        cls,
        *,
        business_logic: Path | TextIO,
        choices: Path | TextIO,
        forms: Path | TextIO,
        questions: Path | TextIO,
    ) -> DataDictionary:
        """Load a data dictionary from individual CSV files."""

        return DataDictionary(
            business_logic=cls._load_csv(business_logic),
            choices=cls._load_csv(choices),
            forms=cls._load_csv(forms),
            questions=cls._load_csv(questions),
        )

    @classmethod
    def from_directory(cls, directory: Path | str) -> DataDictionary:
        """Load all required CSV files from ``directory``."""

        dir_path = Path(directory)
        paths = {attr: dir_path / name for name, attr in cls.REQUIRED_FILES.items()}
        return cls.from_files(**paths)

    @classmethod
    def from_zip(cls, source: Path | BinaryIO) -> DataDictionary:
        """Load a data dictionary from a ZIP archive containing the required CSVs."""

        with zipfile.ZipFile(source) as zf:
            data: dict[str, list[dict[str, str]]] = {}
            for name, attr in cls.REQUIRED_FILES.items():
                with zf.open(name) as fh:
                    with io.TextIOWrapper(fh, encoding="utf-8") as text_fh:
                        data[attr] = cls._load_csv(text_fh)
        return DataDictionary(**data)
