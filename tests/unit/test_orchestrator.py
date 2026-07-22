"""Tests for MultiStudyOrchestrator discovery and filtering behavior."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from imednet.core.context import get_current_study
from imednet.errors import FilterConflictError
from imednet.models.studies import Study
from imednet.orchestration.logging import StudyContextLogAdapter
from imednet.orchestration.orchestrator import MultiStudyOrchestrator


def _make_study(study_key: str) -> Study:
    """Helper function to  make study."""
    return Study(study_key=study_key)


def _mock_monotonic(monkeypatch: pytest.MonkeyPatch, values: list[float]) -> None:
    """Helper function to  mock monotonic."""

    def infinite_clock():
        """Helper function to infinite clock."""
        yield from values
        last_v = values[-1] if values else 0.0
        while True:
            last_v += 0.01
            yield last_v

    clock_values = infinite_clock()
    monkeypatch.setattr(
        "imednet.orchestration.orchestrator.time.monotonic",
        lambda: next(clock_values),
    )


def test_orchestrator_is_instantiable_with_default_max_workers() -> None:
    """Test that orchestrator is instantiable with default max workers."""
    sdk = MagicMock()

    orchestrator = MultiStudyOrchestrator(sdk)

    assert orchestrator.sdk is sdk
    assert orchestrator.max_workers == 4


def test_orchestrator_raises_for_invalid_max_workers() -> None:
    """Test that orchestrator raises for invalid max workers."""
    sdk = MagicMock()

    with pytest.raises(ValueError, match="max_workers must be >= 1"):
        MultiStudyOrchestrator(sdk, max_workers=0)


def test_resolve_active_studies_returns_all_study_keys() -> None:
    """Test that resolve active studies returns all study keys."""
    sdk = MagicMock()
    sdk.studies.list.return_value = [_make_study("A"), _make_study("B")]
    orchestrator = MultiStudyOrchestrator(sdk)

    result = orchestrator.resolve_active_studies()

    assert result == ["A", "B"]
    sdk.studies.list.assert_called_once_with()


def test_resolve_active_studies_applies_whitelist() -> None:
    """Test that resolve active studies applies whitelist."""
    sdk = MagicMock()
    sdk.studies.list.return_value = [_make_study("A"), _make_study("B")]
    orchestrator = MultiStudyOrchestrator(sdk)

    result = orchestrator.resolve_active_studies(whitelist={"A"})

    assert result == ["A"]


def test_resolve_active_studies_applies_blacklist() -> None:
    """Test that resolve active studies applies blacklist."""
    sdk = MagicMock()
    sdk.studies.list.return_value = [_make_study("A"), _make_study("B")]
    orchestrator = MultiStudyOrchestrator(sdk)

    result = orchestrator.resolve_active_studies(blacklist={"A"})

    assert result == ["B"]


def test_resolve_active_studies_raises_on_conflicting_filters_before_network_call() -> None:
    """Test that resolve active studies raises on conflicting filters before network call."""
    sdk = MagicMock()
    orchestrator = MultiStudyOrchestrator(sdk)

    with pytest.raises(FilterConflictError) as err:
        orchestrator.resolve_active_studies(whitelist={"A"}, blacklist={"B"})

    assert err.value.whitelist == {"A"}
    assert err.value.blacklist == {"B"}
    sdk.studies.list.assert_not_called()


def test_resolve_active_studies_with_empty_filter_sets_returns_all_studies() -> None:
    """Test that resolve active studies with empty filter sets returns all studies."""
    sdk = MagicMock()
    sdk.studies.list.return_value = [_make_study("A"), _make_study("B")]
    orchestrator = MultiStudyOrchestrator(sdk)

    result = orchestrator.resolve_active_studies(whitelist=set(), blacklist=set())

    assert result == ["A", "B"]


def test_execute_pipeline_returns_success_results_and_forwards_worker_arguments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that execute pipeline returns success results and forwards worker arguments."""
    sdk = MagicMock()
    sdk.studies.list.return_value = [_make_study("A"), _make_study("B")]
    orchestrator = MultiStudyOrchestrator(sdk, max_workers=2)
    _mock_monotonic(monkeypatch, [0.0, 0.01, 0.02, 0.03])

    def worker(
        study_key: str,
        sdk_client: MagicMock,
        study_logger: StudyContextLogAdapter,
        suffix: str,
        *,
        scale: int,
    ) -> str:
        """Helper function to worker."""
        assert sdk_client is sdk
        assert study_logger.study_key == study_key
        return f"{study_key}-{suffix}-{scale}"

    results = orchestrator.execute_pipeline(worker, suffix="done", scale=2)

    assert set(results) == {"A", "B"}
    for study_key, result in results.items():
        assert result["status"] == "SUCCESS"
        assert result["data"] == f"{study_key}-done-2"
        assert result["error"] is None
        assert result["duration_seconds"] > 0


def test_execute_pipeline_isolates_per_study_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that execute pipeline isolates per study failures."""
    sdk = MagicMock()
    sdk.studies.list.return_value = [_make_study("A"), _make_study("B"), _make_study("C")]
    orchestrator = MultiStudyOrchestrator(sdk, max_workers=3)
    _mock_monotonic(monkeypatch, [0.0, 0.01, 0.02, 0.03, 0.04, 0.05])

    def worker(
        study_key: str, _sdk_client: MagicMock, _study_logger: StudyContextLogAdapter
    ) -> str:
        """Helper function to worker."""
        if study_key == "B":
            raise RuntimeError("boom")
        return f"ok-{study_key}"

    results = orchestrator.execute_pipeline(worker)

    assert set(results) == {"A", "B", "C"}
    assert results["B"]["status"] == "FAILED"
    assert results["B"]["data"] is None
    assert results["B"]["error"] == "RuntimeError('boom')"
    assert results["B"]["duration_seconds"] > 0

    for study_key in ("A", "C"):
        assert results[study_key]["status"] == "SUCCESS"
        assert results[study_key]["data"] == f"ok-{study_key}"
        assert results[study_key]["error"] is None
        assert results[study_key]["duration_seconds"] > 0


def test_execute_pipeline_propagates_study_context_to_worker_thread(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Pipeline functions can call get_current_study() without an explicit study_key."""
    sdk = MagicMock()
    sdk.studies.list.return_value = [_make_study("ALPHA"), _make_study("BETA")]
    orchestrator = MultiStudyOrchestrator(sdk, max_workers=2)
    _mock_monotonic(monkeypatch, [0.0, 0.01, 0.02, 0.03])

    def worker(
        study_key: str,
        sdk_client: MagicMock,
        study_logger: StudyContextLogAdapter,
    ) -> str:
        """Helper function to worker."""
        # get_current_study() must resolve to the same key passed explicitly.
        return get_current_study()

    results = orchestrator.execute_pipeline(worker)

    assert set(results) == {"ALPHA", "BETA"}
    for study_key, result in results.items():
        assert result["status"] == "SUCCESS"
        assert result["data"] == study_key


def test_sdk_property_returns_original_sdk() -> None:
    """Test that sdk property returns original sdk."""
    sdk = MagicMock()
    orchestrator = MultiStudyOrchestrator(sdk)
    assert orchestrator.sdk is sdk


def test_max_workers_property_returns_configured_value() -> None:
    """Test that max workers property returns configured value."""
    sdk = MagicMock()
    orchestrator = MultiStudyOrchestrator(sdk, max_workers=7)
    assert orchestrator.max_workers == 7


def test_resolve_active_studies_logs_and_returns_all_when_no_filters(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that resolve active studies logs and returns all when no filters."""
    sdk = MagicMock()
    sdk.studies.list.return_value = [_make_study("A"), _make_study("B")]
    orchestrator = MultiStudyOrchestrator(sdk)

    with caplog.at_level("DEBUG", logger="imednet.orchestration.orchestrator"):
        result = orchestrator.resolve_active_studies()

    assert result == ["A", "B"]
    assert "Resolved 2 studies from registry." in caplog.text


def test_resolve_active_studies_logs_whitelist_selection(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that resolve active studies logs whitelist selection."""
    sdk = MagicMock()
    sdk.studies.list.return_value = [_make_study("A"), _make_study("B"), _make_study("C")]
    orchestrator = MultiStudyOrchestrator(sdk)

    with caplog.at_level("INFO", logger="imednet.orchestration.orchestrator"):
        result = orchestrator.resolve_active_studies(whitelist={"A", "C"})

    assert result == ["A", "C"]
    assert "Whitelist filter applied: 2/3 studies selected." in caplog.text


def test_resolve_active_studies_logs_blacklist_selection(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that resolve active studies logs blacklist selection."""
    sdk = MagicMock()
    sdk.studies.list.return_value = [_make_study("A"), _make_study("B"), _make_study("C")]
    orchestrator = MultiStudyOrchestrator(sdk)

    with caplog.at_level("INFO", logger="imednet.orchestration.orchestrator"):
        result = orchestrator.resolve_active_studies(blacklist={"B"})

    assert result == ["A", "C"]
    assert "Blacklist filter applied: 2/3 studies selected." in caplog.text
