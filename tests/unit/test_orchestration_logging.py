"""Tests for study-context orchestration logging adapters."""

from __future__ import annotations

import logging
from typing import Any

from imednet.orchestration import StudyContextLogAdapter, make_study_logger


def test_study_context_log_adapter_exposes_study_key() -> None:
    """Test the test study context log adapter exposes study key functionality."""
    adapter = StudyContextLogAdapter(logging.getLogger("tests"), study_key="PROT-01")
    assert adapter.study_key == "PROT-01"


def test_study_context_log_adapter_process_injects_study_key() -> None:
    """Test the test study context log adapter process injects study key functionality."""
    adapter = StudyContextLogAdapter(logging.getLogger("tests"), study_key="PROT-01")

    msg, kwargs = adapter.process("msg", {})

    assert msg == "msg"
    assert kwargs["extra"]["study_key"] == "PROT-01"


def test_study_context_log_adapter_process_overrides_extra_study_key() -> None:
    """Test the test study context log adapter process overrides extra study key functionality."""
    adapter = StudyContextLogAdapter(logging.getLogger("tests"), study_key="PROT-01")
    kwargs: dict[str, Any] = {"extra": {"study_key": "OTHER", "x": 1}}

    _, processed = adapter.process("msg", kwargs)

    assert processed["extra"]["study_key"] == "PROT-01"
    assert processed["extra"]["x"] == 1
    assert kwargs["extra"]["study_key"] == "OTHER"


def test_make_study_logger_uses_orchestration_logger() -> None:
    """Test the test make study logger uses orchestration logger functionality."""
    adapter = make_study_logger("PROT-01")
    assert isinstance(adapter, StudyContextLogAdapter)
    assert adapter.study_key == "PROT-01"
    assert adapter.logger.name == "imednet.orchestration"
