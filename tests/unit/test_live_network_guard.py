"""Regression tests: block_external_requests must not activate respx for live tests.

These tests use pytest's ``pytester`` fixture to run a tiny in-process pytest
session and assert that the fixture override in ``tests/live/conftest.py``
actually prevents ``respx_mock`` from intercepting real HTTP traffic during
live-suite runs.
"""
from __future__ import annotations

import pytest

pytest_plugins = ["pytester"]


def test_block_external_requests_bypassed_in_live_suite(pytester: pytest.Pytester) -> None:
    """Overriding block_external_requests in live/conftest.py must suppress respx_mock.

    Simulates the exact structure of ``tests/`` + ``tests/live/`` and verifies
    that a live test can reach the network (or at least fail with a real
    connection error) instead of an ``AllMockedAssertionError``.
    """
    pytester.makeini(
        """
[pytest]
asyncio_mode = auto
markers =
    live: marks tests that require a live external connection
"""
    )

    # Root conftest mirrors the real tests/conftest.py guard.
    pytester.makeconftest(
        """
import pytest

@pytest.fixture(autouse=True)
def block_external_requests(request):
    if request.node.get_closest_marker("live"):
        yield
        return
    request.getfixturevalue("respx_mock")
    yield
"""
    )

    # Nested live/ package with the override fixture.
    live_dir = pytester.mkpydir("live")
    (live_dir / "conftest.py").write_text(
        """
import pytest
from typing import Generator

pytestmark = pytest.mark.live

@pytest.fixture(autouse=True)
def block_external_requests() -> Generator[None, None, None]:
    # Override: live tests are allowed to make real HTTP calls.
    yield
""",
        encoding="utf-8",
    )

    # A live test that would raise AllMockedAssertionError if respx were active.
    (live_dir / "test_guard.py").write_text(
        """
import httpx
import pytest
from respx.models import AllMockedAssertionError

@pytest.mark.live
def test_no_respx_blocking_in_live_suite():
    \"\"\"Real (or refused) connections must not be intercepted by respx.\"\"\"
    try:
        # Port 1 is almost universally refused; this just needs to NOT raise
        # AllMockedAssertionError – a refused connection proves respx is inactive.
        httpx.get("http://127.0.0.1:1", timeout=1.0)
    except AllMockedAssertionError as exc:
        pytest.fail(
            f"respx is still intercepting live requests; "
            f"the network guard was not bypassed: {exc}"
        )
    except Exception:
        # Any real network error (ConnectError, TimeoutException, …) is fine.
        pass
""",
        encoding="utf-8",
    )

    result = pytester.runpytest_subprocess("live/", "-v")
    result.assert_outcomes(passed=1)


def test_block_external_requests_active_outside_live_suite(pytester: pytest.Pytester) -> None:
    """Sanity-check: respx_mock must still block requests in non-live tests."""
    pytester.makeini(
        """
[pytest]
asyncio_mode = auto
markers =
    live: marks tests that require a live external connection
"""
    )

    pytester.makeconftest(
        """
import pytest

@pytest.fixture(autouse=True)
def block_external_requests(request):
    if request.node.get_closest_marker("live"):
        yield
        return
    request.getfixturevalue("respx_mock")
    yield
"""
    )

    # A plain (non-live) test that should be blocked by respx_mock.
    pytester.makepyfile(
        test_unit_guard="""
import httpx
import pytest
from respx.models import AllMockedAssertionError

def test_respx_blocks_non_live_requests():
    with pytest.raises(AllMockedAssertionError):
        httpx.get("http://127.0.0.1:1", timeout=1.0)
"""
    )

    result = pytester.runpytest_subprocess("-v")
    result.assert_outcomes(passed=1)
