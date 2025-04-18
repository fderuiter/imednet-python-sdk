"""Site-related data models."""

from datetime import datetime

from pydantic import BaseModel, Field


class SiteModel(BaseModel):
    """Model representing a site in the iMednet system."""

    studyKey: str = Field(..., description="Unique study key for the given study")
    siteId: int = Field(..., description="Unique system identifier for the site")
    siteName: str = Field(..., description="Name of the site")
    siteEnrollmentStatus: str = Field(..., description="Current enrollment status of the site")
    dateCreated: datetime = Field(..., description="Date when the site record was created")
    dateModified: datetime = Field(..., description="Last modification date of the site record")
