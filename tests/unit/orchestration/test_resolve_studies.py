"""TODO: Add docstring."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from imednet.errors import FilterConflictError
from imednet.orchestration import MultiStudyOrchestrator


def test_resolve_all_studies(orchestrator: MultiStudyOrchestrator) -> None:
    """TODO: Add docstring."""
    assert orchestrator.resolve_active_studies() == ["STUDY-A", "STUDY-B", "STUDY-C"]


def test_whitelist_filter(orchestrator: MultiStudyOrchestrator) -> None:
    """TODO: Add docstring."""
    assert orchestrator.resolve_active_studies(whitelist={"STUDY-A"}) == ["STUDY-A"]


def test_blacklist_filter(orchestrator: MultiStudyOrchestrator) -> None:
    """TODO: Add docstring."""
    assert orchestrator.resolve_active_studies(blacklist={"STUDY-A"}) == [
        "STUDY-B",
        "STUDY-C",
    ]


def test_whitelist_with_nonexistent_key(orchestrator: MultiStudyOrchestrator) -> None:
    """TODO: Add docstring."""
    assert orchestrator.resolve_active_studies(whitelist={"NONEXISTENT"}) == []


def test_blacklist_excludes_all(orchestrator: MultiStudyOrchestrator) -> None:
    """TODO: Add docstring."""
    assert (
        orchestrator.resolve_active_studies(blacklist={"STUDY-A", "STUDY-B", "STUDY-C"})
        == []
    )


def test_filter_conflict_raises(orchestrator: MultiStudyOrchestrator) -> None:
    """TODO: Add docstring."""
    with pytest.raises(FilterConflictError):
        orchestrator.resolve_active_studies(
            whitelist={"STUDY-A"}, blacklist={"STUDY-B"}
        )


def test_filter_conflict_error_attributes(orchestrator: MultiStudyOrchestrator) -> None:
    """TODO: Add docstring."""
    whitelist = {"STUDY-A"}
    blacklist = {"STUDY-B"}

    with pytest.raises(FilterConflictError) as exc_info:
        orchestrator.resolve_active_studies(whitelist=whitelist, blacklist=blacklist)

    assert exc_info.value.whitelist == whitelist
    assert exc_info.value.blacklist == blacklist


def test_filter_conflict_raised_before_api_call(mock_sdk: MagicMock) -> None:
    """TODO: Add docstring."""
    orchestrator = MultiStudyOrchestrator(mock_sdk)

    with pytest.raises(FilterConflictError):
        orchestrator.resolve_active_studies(
            whitelist={"STUDY-A"}, blacklist={"STUDY-B"}
        )

    mock_sdk.studies.list.assert_not_called()


def test_max_workers_validation(mock_sdk: MagicMock) -> None:
    """TODO: Add docstring."""
    with pytest.raises(ValueError, match="max_workers must be >= 1"):
        MultiStudyOrchestrator(mock_sdk, max_workers=0)


def test_sdk_stored_as_reference(
    mock_sdk: MagicMock, orchestrator: MultiStudyOrchestrator
) -> None:
    """TODO: Add docstring."""
    assert orchestrator.sdk is mock_sdk
