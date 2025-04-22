"""Pydantic models related to iMednet Sites.

This module defines the Pydantic model `SiteModel` which represents the
structure of site information retrieved from the iMednet API, typically
via the `/sites` endpoint.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class SiteModel(BaseModel):
    """Represents a clinical research site within a study in iMednet.

    This model captures key information about a site, including its identifiers,
    name, status, and creation/modification dates.

    Attributes:
        studyKey: Unique identifier for the study this site belongs to.
        siteId: Unique numeric identifier assigned by iMednet to this site.
        siteName: The name of the site.
        siteEnrollmentStatus: The current enrollment status of the site (e.g., "Active",
                              "Inactive", "Recruiting").
        dateCreated: The date and time when the site record was initially created.
        dateModified: The date and time when the site record was last modified.
    """

    studyKey: str = Field(..., description="Unique study key for the given study")
    siteId: int = Field(..., description="Unique system identifier for the site")
    siteName: str = Field(..., description="Name of the site")
    siteEnrollmentStatus: str = Field(..., description="Current enrollment status of the site")
    dateCreated: datetime = Field(..., description="Date when the site record was created")
    dateModified: datetime = Field(..., description="Last modification date of the site record")
