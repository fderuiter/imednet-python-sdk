"""TODO: Add docstring."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from imednet.models.json_base import JsonModel


class Site(JsonModel):
    """TODO: Add docstring."""

    study_key: Optional[str] = Field(default=None, alias="studyKey")
    site_id: Optional[int] = Field(default=None, alias="siteId")
    site_name: Optional[str] = Field(default=None, alias="siteName")
    site_enrollment_status: Optional[str] = Field(default=None, alias="siteEnrollmentStatus")
    date_created: Optional[str] = Field(default=None, alias="dateCreated")
    date_modified: Optional[str] = Field(default=None, alias="dateModified")

    pass
