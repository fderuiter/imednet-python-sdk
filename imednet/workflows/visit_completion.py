"""Workflow for summarizing visit completion for a subject."""

from typing import TYPE_CHECKING, Dict

from ..utils.filters import build_filter_string
from .study_structure import get_study_structure

if TYPE_CHECKING:  # pragma: no cover - import for type checking only
    from ..sdk import ImednetSDK


class VisitCompletionWorkflow:
    """Provide utilities for assessing visit completion for a subject."""

    def __init__(self, sdk: "ImednetSDK") -> None:
        self._sdk = sdk

    def get_subject_progress(self, study_key: str, subject_key: str) -> Dict[str, Dict[str, str]]:
        """Return record status for all expected visit/forms for a subject."""
        structure = get_study_structure(self._sdk, study_key)
        filter_str = build_filter_string({"subject_key": subject_key})
        records = self._sdk.records.list(study_key, filter=filter_str)

        record_status_map: Dict[tuple[int, int], str] = {}
        for rec in records:
            record_status_map[(rec.interval_id, rec.form_id)] = rec.record_status

        progress: Dict[str, Dict[str, str]] = {}
        for interval in structure.intervals:
            form_progress: Dict[str, str] = {}
            for form in interval.forms:
                status = record_status_map.get((interval.interval_id, form.form_id), "MISSING")
                form_progress[form.form_key] = status
            progress[interval.interval_name] = form_progress

        return progress
