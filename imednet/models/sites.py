from __future__ import annotations

from datetime import datetime

from pydantic import Field

from imednet.models.json_base import JsonModel


class Site(JsonModel):
    """Represents a single clinical site participating in a study."""

    study_key: str = Field("", alias="studyKey", description="The key of the study.")
    site_id: int = Field(0, alias="siteId", description="The ID of the site.")
    site_name: str = Field("", alias="siteName", description="The name of the site.")
    site_enrollment_status: str = Field(
        "", alias="siteEnrollmentStatus", description="The enrollment status of the site."
    )
    date_created: datetime = Field(
        default_factory=datetime.now,
        alias="dateCreated",
        description="The date the site was created.",
    )
    date_modified: datetime = Field(
        default_factory=datetime.now,
        alias="dateModified",
        description="The date the site was last modified.",
    )
