"""Thread- and task-local study context helpers."""

from __future__ import annotations

import contextvars
from contextlib import contextmanager
from typing import Iterator, Optional

from imednet.errors.validation import ConfigurationError

_active_study: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "active_study", default=None
)


def set_study_context(study_key: str) -> contextvars.Token[Optional[str]]:
    """Set the active study key for the current thread/task context."""
    return _active_study.set(study_key)


def reset_study_context(token: contextvars.Token[Optional[str]]) -> None:
    """Reset the active study key using a token from :func:`set_study_context`."""
    _active_study.reset(token)


def clear_study_context() -> None:
    """Clear the active study key for the current thread/task context."""
    _active_study.set(None)


def get_study_context() -> Optional[str]:
    """Get the current study key for the active thread/task context."""
    return _active_study.get()


def get_current_study() -> str:
    """Get the current study key or raise when no study context is set."""
    study = _active_study.get()
    if not study:
        raise ConfigurationError(
            "No study key provided. You must either pass 'study_key' explicitly "
            "to the endpoint method or set it using ImednetSDK.study_context(...)."
        )
    return study


@contextmanager
def study_context(study_key: str) -> Iterator[None]:
    """Temporarily set the active study key for the current thread/task context."""
    token = set_study_context(study_key)
    try:
        yield
    finally:
        reset_study_context(token)


class Context:
    """Compatibility shim backed by thread/task-local context variables."""

    @property
    def default_study_key(self) -> Optional[str]:
        """TODO: Add docstring."""
        return _active_study.get()

    def set_default_study_key(self, study_key: str) -> None:
        """TODO: Add docstring."""
        _active_study.set(study_key)

    def clear_default_study_key(self) -> None:
        """TODO: Add docstring."""
        clear_study_context()
