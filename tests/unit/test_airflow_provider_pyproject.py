from pathlib import Path


def test_airflow_provider_dependencies_are_runtime_safe() -> None:
    pyproject_path = (
        Path(__file__).resolve().parents[2] / "packages" / "providers-airflow" / "pyproject.toml"
    )
    content = pyproject_path.read_text(encoding="utf-8")

    assert 'apache-airflow = ">=2.3.0,<4.0.0"' in content
    assert 'apache-airflow-providers-amazon = { version = ">=8.0.0", optional = true }' in content
    assert "[tool.poetry.extras]" in content
    assert 'amazon = ["apache-airflow-providers-amazon"]' in content


def test_workspace_dev_group_includes_airflow_for_tooling() -> None:
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    content = pyproject_path.read_text(encoding="utf-8")

    assert (
        'apache-airflow = { version = ">=3.2.1,<4.0.0", python = ">=3.10,<3.15 || >3.15,<4.0" }'
        in content
    )
