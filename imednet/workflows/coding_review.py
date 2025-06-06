"""Workflow utilities for reviewing coding completeness and consistency."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from ..models import Coding
from ..utils.filters import build_filter_string

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from ..sdk import ImednetSDK


class CodingReviewWorkflow:
    """Helpers for retrieving codings and identifying issues."""

    def __init__(self, sdk: "ImednetSDK") -> None:
        self._sdk = sdk

    def list_codings(
        self,
        study_key: str,
        coding_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **kwargs: Any,
    ) -> List[Coding]:
        """Return codings for a study using optional filter criteria."""
        filter_str = build_filter_string(coding_filter) if coding_filter else None
        return self._sdk.codings.list(study_key, filter=filter_str, **kwargs)

    def get_uncoded_items(
        self,
        study_key: str,
        coding_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **kwargs: Any,
    ) -> List[Coding]:
        """Return codings missing a code value."""
        codings = self.list_codings(study_key, coding_filter, **kwargs)
        return [c for c in codings if not c.code]

    def get_inconsistent_codings(
        self,
        study_key: str,
        coding_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **kwargs: Any,
    ) -> List[Coding]:
        """Return codings where the same variable/value pair has multiple codes."""
        codings = self.list_codings(study_key, coding_filter, **kwargs)
        groups: Dict[Tuple[str, str], List[Coding]] = {}
        for coding in codings:
            key = (coding.variable, coding.value)
            groups.setdefault(key, []).append(coding)

        inconsistent: List[Coding] = []
        for items in groups.values():
            codes = {c.code for c in items if c.code}
            if len(codes) > 1:
                inconsistent.extend(items)

        return inconsistent


# Integration:
# - Import :class:`CodingReviewWorkflow` from ``imednet.workflows`` or initialize
#   directly via ``sdk.workflows`` when available.
