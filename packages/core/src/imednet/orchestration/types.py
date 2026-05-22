"""Type protocols and result schemas for the MultiStudyOrchestrator engine."""

from __future__ import annotations

from typing import Any, TypeVar

from typing_extensions import Protocol, TypedDict, runtime_checkable

T_Output = TypeVar("T_Output", covariant=True)


@runtime_checkable
class StudyWorkerCallable(Protocol[T_Output]):
    """Defines the explicit signature required for injected pipeline tasks.

    Pipeline callables injected into ``MultiStudyOrchestrator.execute_pipeline``
    must conform to this protocol.
    """

    def __call__(
        self,
        study_key: str,
        sdk_client: Any,
        logger: Any,
        *args: Any,
        **kwargs: Any,
    ) -> T_Output: ...


class OrchestratorResult(TypedDict, total=False):
    """Normalized result entry returned per study by ``execute_pipeline``."""

    status: str
    data: Any | None
    error: str | None
    duration_seconds: float


__all__ = [
    "StudyWorkerCallable",
    "OrchestratorResult",
    "T_Output",
]
