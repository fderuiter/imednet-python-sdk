"""TODO: Add docstring."""
from __future__ import annotations

from typing import Callable
from unittest.mock import MagicMock

import pytest

from imednet.orchestration import MultiStudyOrchestrator


@pytest.fixture
def mock_study() -> Callable[[str], MagicMock]:
    """Factory fixture: create a mock Study-like object with a study_key."""

    def _make(study_key: str) -> MagicMock:
        """TODO: Add docstring."""
        study = MagicMock()
        study.study_key = study_key
        return study

    return _make


@pytest.fixture
def mock_sdk(request: pytest.FixtureRequest) -> MagicMock:
    """Mock ImednetSDK with a configurable study list."""
    study_keys: list[str] = getattr(request, "param", ["STUDY-A", "STUDY-B", "STUDY-C"])
    sdk = MagicMock()
    sdk.studies.list.return_value = [MagicMock(study_key=key) for key in study_keys]
    return sdk


@pytest.fixture
def orchestrator(mock_sdk: MagicMock) -> MultiStudyOrchestrator:
    """TODO: Add docstring."""
    return MultiStudyOrchestrator(mock_sdk, max_workers=3)
