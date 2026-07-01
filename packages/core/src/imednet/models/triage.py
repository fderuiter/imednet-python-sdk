"""Models for triage and reviewer workflows."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from msgspec import field as Field

from imednet.models.json_base import JsonModel


class TriageStatus(str, Enum):
    """Enumeration of possible triage statuses."""

    NEW = "NEW"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"


class TriageAnnotation(JsonModel, kw_only=True, omit_defaults=True):
    """Reviewer note attached to a triage item."""

    annotation_id: str 
    user_id: str 
    comment: str 
    timestamp: datetime
    def __post_init__(self):
        import msgspec
        if not self.annotation_id or not self.annotation_id.strip():
            raise msgspec.ValidationError("annotation_id cannot be blank")





class TriageHistoryEntry(JsonModel, kw_only=True, omit_defaults=True):
    """Status transition audit entry for a triage item."""

    transition_id: str 
    from_status: TriageStatus
    to_status: TriageStatus
    user_id: str 
    comment: Optional[str] = None
    timestamp: datetime





class TriageItem(JsonModel, kw_only=True, omit_defaults=True):
    """Core triage item used by queue and reviewer workflows."""

    item_id: str 
    study_key: str 
    status: TriageStatus = TriageStatus.NEW
    assignee: Optional[str] = None
    severity: str 
    annotations: list[TriageAnnotation] = Field(default_factory=list)
    history: list[TriageHistoryEntry] = Field(default_factory=list)
