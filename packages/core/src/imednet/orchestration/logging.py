"""Per-study logging adapter for the MultiStudyOrchestrator engine.

This module provides :class:`StudyContextLogAdapter`, which enriches every log
record emitted by a worker thread with ``study_key`` and ``studyKey`` fields.
When combined
with a JSON formatter (e.g. :func:`~imednet.utils.json_logging.configure_json_logging`),
each log line carries structured metadata that can be indexed by log
aggregation systems such as Splunk, Datadog, or CloudWatch Logs.

Example JSON output
-------------------

With JSON logging enabled the adapter produces records like::

    {
        "timestamp": "2024-01-15T10:23:45.123456Z",
        "level": "INFO",
        "logger": "imednet.orchestration",
        "message": "Starting data extraction",
        "study_key": "PROT-01",
        "studyKey": "PROT-01"
    }

Usage::

    from imednet.orchestration.logging import make_study_logger

    study_logger = make_study_logger("PROT-01")
    study_logger.info("Starting data extraction")
    # → emits a record with extra={"study_key": "PROT-01", "studyKey": "PROT-01"}
"""

from __future__ import annotations

import logging
from collections.abc import MutableMapping
from typing import Any


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    _AdapterBase = logging.LoggerAdapter[logging.Logger]
else:
    _AdapterBase = logging.LoggerAdapter

class StudyContextLogAdapter(_AdapterBase):
    """A logger adapter that enriches records with a bound study key."""

    def __init__(self, logger: logging.Logger, study_key: str) -> None:
        """Initialize the study context log adapter.

        Args:
            logger: The underlying logger to wrap.
            study_key: The study identifier to inject into every log record.
        """
        super().__init__(logger, extra={"study_key": study_key})
        self._study_key = study_key

    @property
    def study_key(self) -> str:
        """The study identifier bound to this adapter."""
        return self._study_key

    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> tuple[Any, MutableMapping[str, Any]]:
        """Inject ``study_key`` and ``studyKey`` into the log record ``extra`` mapping."""
        kwargs = dict(kwargs)
        extra = dict(kwargs.get("extra", {}))
        extra["study_key"] = self._study_key
        extra["studyKey"] = self._study_key
        kwargs["extra"] = extra
        return msg, kwargs


def make_study_logger(study_key: str) -> StudyContextLogAdapter:
    """Create a :class:`StudyContextLogAdapter` for a study key.

    Args:
        study_key: The study identifier to bind to log records.

    Returns:
        A logger adapter that enriches records with the study key.
    """
    return StudyContextLogAdapter(logging.getLogger("imednet.orchestration"), study_key)


__all__ = ["StudyContextLogAdapter", "make_study_logger"]
