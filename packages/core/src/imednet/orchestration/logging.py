"""Per-study logging adapter for the MultiStudyOrchestrator engine."""

from __future__ import annotations

import logging
from typing import Any, MutableMapping


class StudyContextLogAdapter(logging.LoggerAdapter):
    """A logger adapter that enriches records with a bound study key."""

    def __init__(self, logger: logging.Logger, study_key: str) -> None:
        super().__init__(logger, extra={"study_key": study_key})
        self._study_key = study_key

    @property
    def study_key(self) -> str:
        """The study identifier bound to this adapter."""
        return self._study_key

    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> tuple[Any, MutableMapping[str, Any]]:
        """Inject ``study_key`` into the log record ``extra`` mapping."""
        extra = kwargs.get("extra", {})
        extra["study_key"] = self._study_key
        kwargs["extra"] = extra
        return msg, kwargs


def make_study_logger(study_key: str) -> StudyContextLogAdapter:
    """Create a :class:`StudyContextLogAdapter` for a study key."""
    return StudyContextLogAdapter(logging.getLogger("imednet.orchestration"), study_key)


__all__ = ["StudyContextLogAdapter", "make_study_logger"]
