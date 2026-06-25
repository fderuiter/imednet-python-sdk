"""Tests for orchestration type contracts and exports."""

from __future__ import annotations

from typing import Any

from imednet.orchestration import OrchestratorResult, StudyWorkerCallable


def _worker(study_key: str, sdk_client: Any, logger: Any, *args: Any, **kwargs: Any) -> int:
    """Test the worker functionality."""
    _ = (study_key, sdk_client, logger, args, kwargs)
    return 1


def test_study_worker_callable_runtime_check() -> None:
    """Test the test study worker callable runtime check functionality."""
    assert isinstance(_worker, StudyWorkerCallable)


def test_non_callable_does_not_satisfy_study_worker_callable() -> None:
    """Test the test non callable does not satisfy study worker callable functionality."""
    assert not isinstance("not-a-worker", StudyWorkerCallable)


def test_orchestrator_result_allows_partial_keys() -> None:
    """Test the test orchestrator result allows partial keys functionality."""
    result: OrchestratorResult = {"status": "SUCCESS", "duration_seconds": 0.5}
    assert result["status"] == "SUCCESS"
    assert result["duration_seconds"] == 0.5
