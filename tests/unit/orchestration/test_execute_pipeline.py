"""TODO: Add docstring."""

from __future__ import annotations

import logging
from time import sleep
from typing import Any
from unittest.mock import MagicMock

import pytest

from imednet.core.context import get_current_study
from imednet.orchestration import MultiStudyOrchestrator


def test_isolation_study_a_failure_does_not_affect_b_and_c(
    orchestrator: MultiStudyOrchestrator,
) -> None:
    """STUDY-A raises RuntimeError; STUDY-B and STUDY-C must succeed."""

    def pipeline(
        study_key: str, sdk: object, logger: logging.LoggerAdapter, **kwargs: Any
    ) -> str:
        """TODO: Add docstring."""
        if study_key == "STUDY-A":
            raise RuntimeError("Simulated failure")
        return f"processed:{study_key}"

    results = orchestrator.execute_pipeline(pipeline)

    assert results["STUDY-A"]["status"] == "FAILED"
    assert "RuntimeError" in (results["STUDY-A"]["error"] or "")
    assert results["STUDY-B"]["status"] == "SUCCESS"
    assert results["STUDY-B"]["data"] == "processed:STUDY-B"
    assert results["STUDY-C"]["status"] == "SUCCESS"


def test_sdk_immutability_across_threads(mock_sdk: MagicMock) -> None:
    """SDK object identity and state must be unchanged after parallel execution."""
    original_id = id(mock_sdk)

    def pipeline(study_key: str, sdk: object, logger: logging.LoggerAdapter) -> bool:
        """TODO: Add docstring."""
        assert id(sdk) == original_id
        return True

    orch = MultiStudyOrchestrator(mock_sdk, max_workers=3)
    results = orch.execute_pipeline(pipeline)

    assert all(r["status"] == "SUCCESS" for r in results.values())
    assert id(orch.sdk) == original_id


def test_logger_study_key_propagated_to_worker(
    orchestrator: MultiStudyOrchestrator, caplog: pytest.LogCaptureFixture
) -> None:
    """Log records emitted inside workers must carry the correct study_key."""

    def pipeline(study_key: str, sdk: object, logger: logging.LoggerAdapter) -> str:
        """TODO: Add docstring."""
        logger.info("Processing %s", study_key)
        return study_key

    with caplog.at_level(logging.INFO, logger="imednet.orchestration"):
        orchestrator.execute_pipeline(pipeline)

    worker_logs = [record for record in caplog.records if record.msg == "Processing %s"]
    assert worker_logs
    for record in worker_logs:
        assert hasattr(record, "study_key")
        assert record.study_key in {"STUDY-A", "STUDY-B", "STUDY-C"}
        assert hasattr(record, "studyKey")
        assert record.studyKey in {"STUDY-A", "STUDY-B", "STUDY-C"}


def test_result_contains_duration_seconds(orchestrator: MultiStudyOrchestrator) -> None:
    """TODO: Add docstring."""

    def pipeline(study_key: str, sdk: object, logger: logging.LoggerAdapter) -> str:
        """TODO: Add docstring."""
        sleep(0.02)
        return study_key

    results = orchestrator.execute_pipeline(pipeline)

    assert all(result["duration_seconds"] > 0 for result in results.values())


def test_successful_result_error_is_none(orchestrator: MultiStudyOrchestrator) -> None:
    """TODO: Add docstring."""

    def pipeline(study_key: str, sdk: object, logger: logging.LoggerAdapter) -> str:
        """TODO: Add docstring."""
        return study_key

    results = orchestrator.execute_pipeline(pipeline)

    assert all(result["data"] is not None for result in results.values())
    assert all(result["error"] is None for result in results.values())


def test_failed_result_data_is_none(orchestrator: MultiStudyOrchestrator) -> None:
    """TODO: Add docstring."""

    def pipeline(study_key: str, sdk: object, logger: logging.LoggerAdapter) -> str:
        """TODO: Add docstring."""
        raise RuntimeError(f"Boom:{study_key}")

    results = orchestrator.execute_pipeline(pipeline)

    assert all(result["status"] == "FAILED" for result in results.values())
    assert all(result["data"] is None for result in results.values())
    assert all(isinstance(result["error"], str) for result in results.values())


def test_execute_pipeline_respects_whitelist(
    orchestrator: MultiStudyOrchestrator,
) -> None:
    """TODO: Add docstring."""

    def pipeline(study_key: str, sdk: object, logger: logging.LoggerAdapter) -> str:
        """TODO: Add docstring."""
        return study_key

    results = orchestrator.execute_pipeline(pipeline, whitelist={"STUDY-A"})

    assert set(results) == {"STUDY-A"}


def test_execute_pipeline_context_propagation(
    orchestrator: MultiStudyOrchestrator,
) -> None:
    """TODO: Add docstring."""

    def pipeline(study_key: str, sdk: object, logger: logging.LoggerAdapter) -> str:
        """TODO: Add docstring."""
        return get_current_study()

    results = orchestrator.execute_pipeline(pipeline)

    assert all(result["status"] == "SUCCESS" for result in results.values())
    for study_key, result in results.items():
        assert result["data"] == study_key


@pytest.mark.parametrize("mock_sdk", [[]], indirect=True)
def test_empty_study_list_returns_empty_dict(mock_sdk: MagicMock) -> None:
    """TODO: Add docstring."""
    orchestrator = MultiStudyOrchestrator(mock_sdk, max_workers=3)

    results = orchestrator.execute_pipeline(lambda *_args, **_kwargs: True)

    assert results == {}
