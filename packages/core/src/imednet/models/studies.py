"""TODO: Add docstring."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from imednet.models.json_base import JsonModel


class Study(JsonModel):
    """TODO: Add docstring."""

    sponsor_key: Optional[str] = Field(default=None, alias="sponsorKey")
    study_key: Optional[str] = Field(default=None, alias="studyKey")
    study_id: Optional[int] = Field(default=None, alias="studyId")
    study_name: Optional[str] = Field(default=None, alias="studyName")
    study_description: Optional[str] = Field(default=None, alias="studyDescription")
    study_type: Optional[str] = Field(default=None, alias="studyType")
    date_created: Optional[str] = Field(default=None, alias="dateCreated")
    date_modified: Optional[str] = Field(default=None, alias="dateModified")
