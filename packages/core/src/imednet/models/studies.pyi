"""Study metadata models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import Field

from imednet.models.base import ImednetBaseModel
from imednet.models.engine import ModelEngine

class Study(ImednetBaseModel):
    """Represents a clinical study and its metadata."""

    sponsor_key: str | None
    study_key: str | None
    study_id: int | None
    study_name: str | None
    study_description: str | None
    study_type: str | None
    date_created: str | None
    date_modified: str | None
