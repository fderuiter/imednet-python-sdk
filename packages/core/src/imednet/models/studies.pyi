"""Study metadata models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel

class Study(JsonModel):
    """Represents a clinical study and its metadata."""

    sponsor_key: Optional[str]
    study_key: Optional[str]
    study_id: Optional[int]
    study_name: Optional[str]
    study_description: Optional[str]
    study_type: Optional[str]
    date_created: Optional[str]
    date_modified: Optional[str]
