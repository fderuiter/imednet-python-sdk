import re
from pathlib import Path

import imednet


def test_project_version_is_single_source_of_truth() -> None:
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    content = pyproject_path.read_text(encoding="utf-8")

    project_version_match = re.search(
        r"(?ms)^\[project\]\n.*?^version\s*=\s*\"([^\"]+)\"",
        content,
    )
    assert project_version_match is not None
    assert project_version_match.group(1) == imednet.__version__

    poetry_section_match = re.search(
        r"(?ms)^\[tool\.poetry\]\n(.*?)(?=^\[|\Z)",
        content,
    )
    assert poetry_section_match is not None
    poetry_section = poetry_section_match.group(1)

    for redundant_key in ("name", "version", "description", "readme", "authors", "license"):
        assert (
            re.search(rf"^\s*{re.escape(redundant_key)}\s*=", poetry_section, flags=re.MULTILINE)
            is None
        )
