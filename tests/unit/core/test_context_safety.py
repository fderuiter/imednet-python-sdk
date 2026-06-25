"""Test Context Safety module."""

import asyncio
import threading
import time

import pytest

from imednet.core.context import (
    get_current_study,
    reset_study_context,
    set_study_context,
    study_context,
)
from imednet.errors.validation import ConfigurationError


async def async_worker(study_key: str, delay: float) -> str:
    """Implementation detail."""
    token = set_study_context(study_key)
    try:
        await asyncio.sleep(delay)
        return get_current_study()
    finally:
        reset_study_context(token)


@pytest.mark.asyncio
async def test_contextvars_prevents_race_conditions() -> None:
    """Implementation detail."""
    results = await asyncio.gather(
        async_worker("STUDY-A", 0.2),
        async_worker("STUDY-B", 0.1),
        async_worker("STUDY-C", 0.3),
    )
    assert results == ["STUDY-A", "STUDY-B", "STUDY-C"]


def test_study_context_is_visible_inside_worker_thread() -> None:
    """study_context() set inside a worker thread is visible in that same thread."""
    result: list[str | None] = []

    def worker() -> None:
        """Test the worker functionality."""
        with study_context("THREAD-A"):
            result.append(get_current_study())

    t = threading.Thread(target=worker)
    t.start()
    t.join()

    assert result == ["THREAD-A"]


def test_study_context_is_isolated_between_threads() -> None:
    """Each thread has its own context — study keys do not bleed across threads."""
    results: dict[str, str] = {}

    def worker(key: str) -> None:
        """Test the worker functionality."""
        with study_context(key):
            time.sleep(0.05)
            results[key] = get_current_study()

    threads = [threading.Thread(target=worker, args=(k,)) for k in ("X", "Y", "Z")]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results == {"X": "X", "Y": "Y", "Z": "Z"}


def test_study_context_is_reset_after_worker_thread_completes() -> None:
    """The context set inside a thread does not persist once the thread has finished."""
    sentinel: list[str | Exception] = []

    def worker() -> None:
        """Test the worker functionality."""
        with study_context("TRANSIENT"):
            pass  # context manager exits before thread ends

        # After the context manager exits, get_current_study should raise.
        try:
            sentinel.append(get_current_study())
        except ConfigurationError as exc:
            sentinel.append(exc)

    t = threading.Thread(target=worker)
    t.start()
    t.join()

    assert len(sentinel) == 1
    assert isinstance(sentinel[0], ConfigurationError)
