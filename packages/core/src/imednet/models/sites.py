from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Site(JsonModel):
    """A site participating in a study."""

    site_name: Optional[str] = Field(None, alias="siteName")
    site_enrollment_status: Optional[str] = Field(None, alias="siteEnrollmentStatus")


Site = ModelEngine.get_model('Site', Site)
