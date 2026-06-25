"""Test Log Adapter module."""

from __future__ import annotations

import logging
from typing import Any

import pytest

from imednet.orchestration import StudyContextLogAdapter, make_study_logger


def test_process_injects_study_key() -> None:
    """Test the test process injects study key functionality."""
    adapter = StudyContextLogAdapter(logging.getLogger("tests.orchestration"), "PROT-01")

    _, kwargs = adapter.process("msg", {})

    assert kwargs["extra"]["study_key"] == "PROT-01"
    assert kwargs["extra"]["studyKey"] == "PROT-01"


def test_process_preserves_caller_extra() -> None:
    """Test the test process preserves caller extra functionality."""
    adapter = StudyContextLogAdapter(logging.getLogger("tests.orchestration"), "PROT-01")
    input_kwargs: dict[str, Any] = {"extra": {"custom": "value"}}

    _, kwargs = adapter.process("msg", input_kwargs)

    assert kwargs["extra"]["custom"] == "value"
    assert kwargs["extra"]["study_key"] == "PROT-01"
    assert kwargs["extra"]["studyKey"] == "PROT-01"


def test_study_key_property() -> None:
    """Test the test study key property functionality."""
    adapter = StudyContextLogAdapter(logging.getLogger("tests.orchestration"), "PROT-01")

    assert adapter.study_key == "PROT-01"


def test_make_study_logger_returns_adapter() -> None:
    """Test the test make study logger returns adapter functionality."""
    assert isinstance(make_study_logger("X"), StudyContextLogAdapter)


def test_log_emission_includes_study_key(caplog: pytest.LogCaptureFixture) -> None:
    """Test the test log emission includes study key functionality."""
    adapter = make_study_logger("PROT-01")

    with caplog.at_level(logging.INFO, logger="imednet.orchestration"):
        adapter.info("adapter-log")

    assert any(getattr(record, "study_key", None) == "PROT-01" for record in caplog.records)
    assert any(getattr(record, "studyKey", None) == "PROT-01" for record in caplog.records)
