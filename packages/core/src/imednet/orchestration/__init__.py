"""Multi-study orchestration engine for iMednet SDK.

Provides :class:`MultiStudyOrchestrator` for executing pipeline functions
concurrently across multiple iMednet study boundaries with fault isolation,
telemetry context propagation, and normalized result reporting.
"""

from __future__ import annotations

from imednet.orchestration.types import OrchestratorResult, StudyWorkerCallable

__all__ = ["OrchestratorResult", "StudyWorkerCallable"]
