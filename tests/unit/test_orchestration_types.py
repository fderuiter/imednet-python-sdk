"""Tests for orchestration type contracts and exports."""

from __future__ import annotations

from typing import Any

from imednet.orchestration import OrchestratorResult, StudyWorkerCallable


def _worker(study_key: str, sdk_client: Any, logger: Any, *args: Any, **kwargs: Any) -> int:
    del study_key, sdk_client, logger, args, kwargs
    return 1


def test_study_worker_callable_runtime_check() -> None:
    assert isinstance(_worker, StudyWorkerCallable)


def test_orchestrator_result_allows_partial_keys() -> None:
    result: OrchestratorResult = {"status": "SUCCESS", "duration_seconds": 0.5}
    assert result["status"] == "SUCCESS"
    assert result["duration_seconds"] == 0.5
