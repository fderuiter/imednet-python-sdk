"""Workflow utilities for tracking visit completion across subjects."""

from typing import TYPE_CHECKING, Dict

from .visit_completion import VisitCompletionWorkflow

if TYPE_CHECKING:  # pragma: no cover - imported for type checking only
    from ..sdk import ImednetSDK


class VisitTrackingWorkflow:
    """Aggregate visit completion information for multiple subjects."""

    def __init__(self, sdk: "ImednetSDK") -> None:
        self._sdk = sdk
        self._subject_tracker = VisitCompletionWorkflow(sdk)

    def summary_by_subject(self, study_key: str) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Return visit completion progress for every subject in the study."""
        subjects = self._sdk.subjects.list(study_key)
        summary: Dict[str, Dict[str, Dict[str, str]]] = {}
        for subj in subjects:
            summary[subj.subject_key] = self._subject_tracker.get_subject_progress(
                study_key, subj.subject_key
            )
        return summary
