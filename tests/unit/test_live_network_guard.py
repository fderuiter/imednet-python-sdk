"""Unit tests for live network guard."""

import importlib
from pathlib import Path

import pytest

test_conftest = importlib.import_module("tests.conftest")


class _DummyNode:
    """Test suite for  DummyNode."""

    def __init__(self, *, path: Path, has_live_marker: bool = False):
        """Initialize the test object."""
        self.path = path
        self._has_live_marker = has_live_marker

    def get_closest_marker(self, name: str) -> object | None:
        """Helper function to get closest marker."""
        if name == "live" and self._has_live_marker:
            return object()
        return None


class _DummyRequest:
    """Test suite for  DummyRequest."""

    def __init__(self, node: _DummyNode):
        """Initialize the test object."""
        self.node = node
        self.fixture_calls: list[str] = []

    def getfixturevalue(self, fixture_name: str) -> None:
        """Helper function to getfixturevalue."""
        self.fixture_calls.append(fixture_name)


def _run_guard(request: _DummyRequest) -> None:
    """Execute the autouse fixture function directly for deterministic unit assertions."""
    fixture = test_conftest.block_external_requests.__wrapped__
    guard = fixture(request=request)
    next(guard)
    with pytest.raises(StopIteration):
        next(guard)


def test_live_path_bypasses_respx_guard() -> None:
    """Test that live path bypasses respx guard."""
    request = _DummyRequest(
        node=_DummyNode(path=test_conftest.ROOT / "tests" / "live" / "test_a.py")
    )

    _run_guard(request)

    assert request.fixture_calls == []


def test_non_live_path_activates_respx_guard() -> None:
    """Test that non live path activates respx guard."""
    request = _DummyRequest(
        node=_DummyNode(path=test_conftest.ROOT / "tests" / "unit" / "test_a.py")
    )

    _run_guard(request)

    assert request.fixture_calls == ["respx_mock"]


def test_live_marker_bypasses_guard_outside_live_directory() -> None:
    """Test that live marker bypasses guard outside live directory."""
    request = _DummyRequest(
        node=_DummyNode(
            path=test_conftest.ROOT / "tests" / "unit" / "test_a.py",
            has_live_marker=True,
        )
    )

    _run_guard(request)

    assert request.fixture_calls == []
