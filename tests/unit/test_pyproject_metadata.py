"""TODO: Add docstring."""

import re
from pathlib import Path

import imednet


def test_project_version_is_single_source_of_truth() -> None:
    """TODO: Add docstring."""
    pyproject_path = (
        Path(__file__).resolve().parents[2] / "packages" / "core" / "pyproject.toml"
    )
    content = pyproject_path.read_text(encoding="utf-8")

    project_section_match = re.search(
        r"(?ms)^\[project\]\n(.*?)(?=^\[|\Z)",
        content,
    )
    assert project_section_match is not None
    project_section = project_section_match.group(1)

    version_match = re.search(
        r'^\s*version\s*=\s*"([^"]+)"', project_section, flags=re.MULTILINE
    )
    assert version_match is not None
    assert version_match.group(1) == imednet.__version__

    readme_match = re.search(
        r'^\s*readme\s*=\s*"([^"]+)"', project_section, flags=re.MULTILINE
    )
    assert readme_match is not None
    readme_path = pyproject_path.parent / readme_match.group(1)
    assert readme_path.exists()
    assert readme_path.parent == pyproject_path.parent

    for required_key in ("name", "description", "readme", "authors", "license"):
        assert (
            re.search(
                rf"^\s*{re.escape(required_key)}\s*=",
                project_section,
                flags=re.MULTILINE,
            )
            is not None
        )
