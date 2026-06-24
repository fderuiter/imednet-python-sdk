"""Validation script for documentation."""

import ast
import subprocess
import sys
from pathlib import Path


def check_readme_drift() -> bool:
    """Validate that the README.md is in sync with code snippets."""
    print("Checking README drift...")
    result = subprocess.run(
        ["python3", "scripts/sync_readme.py", "--dry-run"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(
            "Error: README.md is out of sync. Please run 'make sync-readme' or 'python3 scripts/sync_readme.py'."
        )
        return True
    print("README.md is up to date.")
    return False


def check_todos_in_init() -> bool:
    """Ensure no TODO strings exist in operator __init__ docstrings."""
    print("Checking for TODOs in __init__ docstrings...")
    base_path = Path("packages/providers-airflow/src/apache_airflow_providers_imednet")
    if not base_path.exists():
        print(f"Warning: Path {base_path} not found.")
        return False

    has_todos = False
    for py_file in base_path.rglob("*.py"):
        content = py_file.read_text()
        try:
            tree = ast.parse(content, filename=str(py_file))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, ast.FunctionDef) and child.name == "__init__":
                        docstring = ast.get_docstring(child)
                        if docstring and "TODO" in docstring:
                            print(
                                f"Error: TODO found in __init__ docstring of class {node.name} in {py_file}"
                            )
                            has_todos = True
    if not has_todos:
        print("No TODOs found in __init__ docstrings.")
    return has_todos


def main():
    """Run validation scripts."""
    drift_failed = check_readme_drift()
    todos_failed = check_todos_in_init()

    if drift_failed or todos_failed:
        print("Validation failed.")
        sys.exit(1)

    print("Validation passed successfully.")
    sys.exit(0)


if __name__ == "__main__":
    main()
