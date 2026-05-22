"""Multi-study orchestration engine for iMednet SDK.

Provides :class:`MultiStudyOrchestrator` for executing pipeline functions
concurrently across multiple iMednet study boundaries with fault isolation,
telemetry context propagation, and normalized result reporting.
"""

from __future__ import annotations

from imednet.orchestration.logging import StudyContextLogAdapter, make_study_logger
from imednet.orchestration.orchestrator import MultiStudyOrchestrator
from imednet.orchestration.types import OrchestratorResult, StudyWorkerCallable

__all__ = [
    "MultiStudyOrchestrator",
    "OrchestratorResult",
    "StudyWorkerCallable",
    "StudyContextLogAdapter",
    "make_study_logger",
]
