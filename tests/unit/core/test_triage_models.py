from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from imednet.models.triage import (
    TriageAnnotation,
    TriageHistoryEntry,
    TriageItem,
    TriageStatus,
)


def test_triage_models_parse_and_strip_whitespace() -> None:
    item = TriageItem.model_validate(
        {
            "item_id": "  AE-1001  ",
            "study_key": "  STUDY-1 ",
            "status": "UNDER_REVIEW",
            "assignee": "  analyst  ",
            "severity": "  critical ",
            "annotations": [
                {
                    "annotation_id": "  a-1 ",
                    "user_id": "  user-1 ",
                    "comment": "  needs follow-up  ",
                    "timestamp": "2024-01-01T00:00:00Z",
                }
            ],
            "history": [
                {
                    "transition_id": "  h-1  ",
                    "from_status": "NEW",
                    "to_status": "UNDER_REVIEW",
                    "user_id": "  user-1 ",
                    "comment": "  started triage  ",
                    "timestamp": "2024-01-01T01:00:00Z",
                }
            ],
        }
    )

    assert item.item_id == "AE-1001"
    assert item.study_key == "STUDY-1"
    assert item.status == TriageStatus.UNDER_REVIEW
    assert item.assignee == "analyst"
    assert item.severity == "critical"
    assert item.annotations[0].comment == "needs follow-up"
    assert item.history[0].comment == "started triage"


def test_triage_history_blank_comment_normalizes_to_none() -> None:
    entry = TriageHistoryEntry.model_validate(
        {
            "transition_id": "h-2",
            "from_status": "UNDER_REVIEW",
            "to_status": "RESOLVED",
            "user_id": "reviewer",
            "comment": "   ",
            "timestamp": datetime(2024, 1, 1, 2, 0, 0),
        }
    )

    assert entry.comment is None


def test_triage_json_roundtrip_keeps_enum_values() -> None:
    annotation = TriageAnnotation(
        annotation_id="a-2",
        user_id="reviewer",
        comment="resolved",
        timestamp=datetime(2024, 1, 2, 0, 0, 0),
    )
    item = TriageItem(
        item_id="PD-44",
        study_key="STUDY-2",
        status=TriageStatus.RESOLVED,
        assignee="manager",
        severity="warning",
        annotations=[annotation],
        history=[],
    )

    dumped = item.model_dump(mode="json")

    assert dumped["status"] == "RESOLVED"
    assert dumped["annotations"][0]["annotation_id"] == "a-2"


def test_triage_models_enforce_schema_constraints() -> None:
    with pytest.raises(ValidationError) as blank_id_error:
        TriageAnnotation.model_validate(
            {
                "annotation_id": "   ",
                "user_id": "reviewer",
                "comment": "valid",
                "timestamp": "2024-01-01T00:00:00Z",
            }
        )
    assert blank_id_error.value.errors()[0]["loc"] == ("annotation_id",)

    with pytest.raises(ValidationError) as status_error:
        TriageItem.model_validate(
            {
                "item_id": "AE-1002",
                "study_key": "STUDY-1",
                "status": "NOT_A_STATUS",
                "assignee": "reviewer",
                "severity": "critical",
                "annotations": [],
                "history": [],
            }
        )
    assert status_error.value.errors()[0]["loc"] == ("status",)
