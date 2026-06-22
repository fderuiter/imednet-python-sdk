"""Exceptions raised by the MultiStudyOrchestrator engine."""

from __future__ import annotations

from imednet.errors.base import ImednetError


class OrchestratorError(ImednetError):
    """Base exception for all orchestration-layer failures.

    Raised when the :class:`~imednet.orchestration.MultiStudyOrchestrator`
    encounters a structural or configuration error that prevents pipeline
    execution from starting.

    Individual per-study runtime failures are NOT raised as exceptions —
    they are captured in the :class:`~imednet.orchestration.OrchestratorResult`
    result matrix with ``status="FAILED"``.
    """


class FilterConflictError(OrchestratorError):
    """Raised when both whitelist and blacklist are non-empty simultaneously.

    The whitelist and blacklist filters are mutually exclusive operations.
    Providing both simultaneously creates ambiguous behavior and is rejected
    at validation time before any study resolution occurs.

    Example::

        # This raises FilterConflictError — a study key cannot be in both:
        orchestrator.execute_pipeline(
            my_func,
            whitelist={"STUDY-A", "STUDY-B"},
            blacklist={"STUDY-C"},
        )
    """

    def __init__(self, whitelist: set[str], blacklist: set[str]) -> None:
        """TODO: Add docstring."""
        super().__init__(
            "Whitelist and blacklist are mutually exclusive. "
            f"Received whitelist={whitelist!r} and blacklist={blacklist!r}. "
            "Provide only one filter type per invocation."
        )
        self.whitelist = whitelist
        self.blacklist = blacklist
