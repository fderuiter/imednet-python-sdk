import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.append(str(Path("/app/scripts")))
import tighten_dependencies as td


def test_compute_upper_bound():
    assert td.compute_upper_bound("0.8.0") == "<0.9.0"
    assert td.compute_upper_bound("1.2.3") == "<1.3.0"
    assert td.compute_upper_bound("2.0.0") == "<2.1.0"


def test_rewrite_spec():
    assert td.rewrite_spec(">=0.8.0,<1.0.0", "0.8.0") == ">=0.8.0,<0.9.0"
    assert td.rewrite_spec(">=0.8.0", "0.8.0") == ">=0.8.0,<0.9.0"
    assert td.rewrite_spec("", "0.8.0") == ">=0.8.0,<0.9.0"
    assert td.rewrite_spec(">=0.8.0,!=0.8.1,<1.0.0", "0.8.0") == ">=0.8.0,!=0.8.1,<0.9.0"


def test_process_dependency():
    internal_pkgs = {"imednet": {"version": "0.8.0"}, "imednet-workflows": {"version": "0.6.0"}}
    assert td.process_dependency("imednet", internal_pkgs) == "imednet>=0.8.0,<0.9.0"
    assert (
        td.process_dependency("imednet[cli]>=0.8.0,<1.0.0", internal_pkgs)
        == "imednet[cli]>=0.8.0,<0.9.0"
    )
    # Should not touch non-internal
    assert td.process_dependency("pandas>=1.0", internal_pkgs) == "pandas>=1.0"
    # Should not match prefix
    assert td.process_dependency("imednet-sinks", internal_pkgs) == "imednet-sinks"
    # Should correctly match hyphens
    assert (
        td.process_dependency("imednet-workflows>=0.5", internal_pkgs)
        == "imednet-workflows>=0.5,<0.7.0"
    )


def test_tighten_file(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("""[project]
name = "my-package"
dependencies = [
    "imednet>=0.8.0",
    "pandas"
]
[project.optional-dependencies]
cli = ["imednet[cli]"]
""")

    internal_pkgs = {"imednet": {"version": "0.8.0", "pyproject_path": pyproject}}

    assert td.tighten_file(pyproject, internal_pkgs) is True

    content = pyproject.read_text()
    assert "imednet>=0.8.0,<0.9.0" in content
    assert "imednet[cli]>=0.8.0,<0.9.0" in content
    assert "pandas" in content

    # Backup should exist
    backup = tmp_path / "pyproject.toml.bak"
    assert backup.exists()


def test_restore_files(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("modified")
    backup = tmp_path / "pyproject.toml.bak"
    backup.write_text("original")

    internal_pkgs = {"imednet": {"version": "0.8.0", "pyproject_path": pyproject}}

    td.restore_files(internal_pkgs)

    assert pyproject.read_text() == "original"
    assert not backup.exists()
