"""Thread- and task-local study context helpers."""

from __future__ import annotations

import contextvars
from typing import Optional

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


def get_current_study() -> str:
    """Get the current study key or raise when no study context is set."""
    study = _active_study.get()
    if not study:
        raise ConfigurationError(
            "No study key provided. You must either pass 'study_key' explicitly "
            "to the endpoint method or set it using ImednetSDK.study_context(...)."
        )
    return study


class Context:
    """Compatibility shim backed by thread/task-local context variables."""

    @property
    def default_study_key(self) -> Optional[str]:
        return _active_study.get()

    def set_default_study_key(self, study_key: str) -> None:
        _active_study.set(study_key)

    def clear_default_study_key(self) -> None:
        clear_study_context()
