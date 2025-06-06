"""Utility workflows for summarizing audit trail data."""

from typing import TYPE_CHECKING, Any, Dict, Optional

from ..utils.filters import build_filter_string

if TYPE_CHECKING:  # pragma: no cover - imported for type checking only
    from ..sdk import ImednetSDK


class AuditAggregationWorkflow:
    """Provide utilities for aggregating record revision information."""

    def __init__(self, sdk: "ImednetSDK") -> None:
        self._sdk = sdk

    def summary_by_user(
        self,
        study_key: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **filters: Any,
    ) -> Dict[str, int]:
        """Return a count of record revisions grouped by user.

        Args:
            study_key: Identifier for the study.
            start_date: Optional start date filter in ``YYYY-MM-DD`` format.
            end_date: Optional end date filter in ``YYYY-MM-DD`` format.
            **filters: Additional filter parameters for the audit trail request.

        Returns:
            Dictionary mapping each user to the number of record revisions they
            performed in the given date range.
        """
        filter_str = build_filter_string(filters) if filters else None

        revisions = self._sdk.record_revisions.list(
            study_key,
            page_size=None,
            filter=filter_str,
            start_date=start_date,
            end_date=end_date,
        )

        summary: Dict[str, int] = {}
        for rev in revisions:
            summary[rev.user] = summary.get(rev.user, 0) + 1

        return summary
