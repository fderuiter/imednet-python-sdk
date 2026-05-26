import re
from pathlib import Path


def test_airflow_provider_dependencies_are_runtime_safe() -> None:
    pyproject_path = (
        Path(__file__).resolve().parents[2] / "packages" / "providers-airflow" / "pyproject.toml"
    )
    content = pyproject_path.read_text(encoding="utf-8")

    assert re.search(r'^apache-airflow\s*=\s*">=2\.3\.0,<4\.0\.0"$', content, re.MULTILINE)
    assert re.search(
        r'^apache-airflow-providers-amazon\s*=\s*\{\s*version\s*=\s*">=8\.0\.0"\s*,\s*optional\s*=\s*true\s*\}$',
        content,
        re.MULTILINE,
    )
    assert re.search(r"^\[tool\.poetry\.extras\]$", content, re.MULTILINE)
    assert re.search(
        r'^amazon\s*=\s*\[\s*"apache-airflow-providers-amazon"\s*\]$',
        content,
        re.MULTILINE,
    )


def test_workspace_dev_group_includes_airflow_for_tooling() -> None:
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    content = pyproject_path.read_text(encoding="utf-8")

    assert re.search(
        (
            r'^apache-airflow\s*=\s*\{\s*version\s*=\s*">=3\.2\.1,<4\.0\.0"\s*,\s*python\s*=\s*'
            r'">=3\.10,<3\.15 \|\| >3\.15,<4\.0"\s*\}$'
        ),
        content,
        re.MULTILINE,
    )
