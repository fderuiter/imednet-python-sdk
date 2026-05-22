"""Tests for MultiStudyOrchestrator discovery and filtering behavior."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from imednet.errors import FilterConflictError
from imednet.orchestration.orchestrator import MultiStudyOrchestrator


def _make_study(study_key: str) -> SimpleNamespace:
    return SimpleNamespace(study_key=study_key)


def test_orchestrator_is_instantiable_with_default_max_workers() -> None:
    sdk = MagicMock()

    orchestrator = MultiStudyOrchestrator(sdk)

    assert orchestrator.sdk is sdk
    assert orchestrator.max_workers == 4


def test_orchestrator_raises_for_invalid_max_workers() -> None:
    sdk = MagicMock()

    with pytest.raises(ValueError, match="max_workers must be >= 1"):
        MultiStudyOrchestrator(sdk, max_workers=0)


def test_resolve_active_studies_returns_all_study_keys() -> None:
    sdk = MagicMock()
    sdk.studies.list.return_value = [_make_study("A"), _make_study("B")]
    orchestrator = MultiStudyOrchestrator(sdk)

    result = orchestrator.resolve_active_studies()

    assert result == ["A", "B"]
    sdk.studies.list.assert_called_once_with()


def test_resolve_active_studies_applies_whitelist() -> None:
    sdk = MagicMock()
    sdk.studies.list.return_value = [_make_study("A"), _make_study("B")]
    orchestrator = MultiStudyOrchestrator(sdk)

    result = orchestrator.resolve_active_studies(whitelist={"A"})

    assert result == ["A"]


def test_resolve_active_studies_applies_blacklist() -> None:
    sdk = MagicMock()
    sdk.studies.list.return_value = [_make_study("A"), _make_study("B")]
    orchestrator = MultiStudyOrchestrator(sdk)

    result = orchestrator.resolve_active_studies(blacklist={"A"})

    assert result == ["B"]


def test_resolve_active_studies_raises_on_conflicting_filters_before_network_call() -> None:
    sdk = MagicMock()
    orchestrator = MultiStudyOrchestrator(sdk)

    with pytest.raises(FilterConflictError):
        orchestrator.resolve_active_studies(whitelist={"A"}, blacklist={"B"})

    sdk.studies.list.assert_not_called()
