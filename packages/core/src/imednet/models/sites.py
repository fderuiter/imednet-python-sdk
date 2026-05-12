from __future__ import annotations

from datetime import datetime

from pydantic import Field

from imednet.models.json_base import JsonModel


class Site(JsonModel):
    """A site participating in a study."""

    study_key: str = Field("", alias="studyKey")
    site_id: int = Field(0, alias="siteId")
    site_name: str = Field("", alias="siteName")
    site_enrollment_status: str = Field("", alias="siteEnrollmentStatus")
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_modified: datetime = Field(default_factory=datetime.now, alias="dateModified")

    pass
