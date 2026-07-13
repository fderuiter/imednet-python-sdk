"""Models for triage and reviewer workflows."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import Field, field_validator

from imednet.models.base import ImednetBaseModel


class TriageStatus(str, Enum):
    """Enumeration of possible triage statuses."""

    NEW = "NEW"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"


class TriageAnnotation(ImednetBaseModel):
    """Reviewer note attached to a triage item."""

    annotation_id: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)
    comment: str = Field(..., min_length=1)
    timestamp: datetime


class TriageHistoryEntry(ImednetBaseModel):
    """Status transition audit entry for a triage item."""

    transition_id: str = Field(..., min_length=1)
    from_status: TriageStatus
    to_status: TriageStatus
    user_id: str = Field(..., min_length=1)
    comment: Optional[str] = None
    timestamp: datetime

    @field_validator("comment", check_fields=False, mode="before")  # type: ignore[untyped-decorator]
    @classmethod
    def _normalise_comment(cls, value: object) -> object:
        """Normalize comment string, returning None if empty or whitespace."""
        if value is None:
            return None
        text = str(value).strip()
        return text or None


class TriageItem(ImednetBaseModel):
    """Core triage item used by queue and reviewer workflows."""

    item_id: str = Field(..., min_length=1)
    study_key: str = Field(..., min_length=1)
    status: TriageStatus = TriageStatus.NEW
    assignee: Optional[str] = None
    severity: str = Field(..., min_length=1)
    annotations: list[TriageAnnotation] = Field(default_factory=list)
    history: list[TriageHistoryEntry] = Field(default_factory=list)
