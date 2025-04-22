"""Pydantic models related to iMednet Studies.

This module defines the Pydantic model `StudyModel` which represents the
structure of study information retrieved from the iMednet API, typically
via the `/studies` endpoint.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StudyModel(BaseModel):
    """Represents a clinical study defined within the iMednet system.

    This model captures high-level information about a study, including its
    identifiers, name, description, type, and creation/modification dates.

    Attributes:
        sponsorKey: The key identifying the sponsor organization for this study.
        studyKey: The unique string identifier assigned to this study.
        studyId: The unique numeric identifier assigned by iMednet to this study.
        studyName: The name of the study.
        studyDescription: An optional detailed description of the study.
        studyType: The type or category of the study.
        dateCreated: The date and time when the study record was initially created.
        dateModified: The date and time when the study record was last modified.
    """

    sponsorKey: str = Field(..., description="Sponsor key that this study belongs to")
    studyKey: str = Field(..., description="Unique study key")
    studyId: int = Field(..., description="Mednet study ID")
    studyName: str = Field(..., description="Study name")
    studyDescription: Optional[str] = Field(None, description="Detailed description of the study")
    studyType: str = Field(..., description="Type of the study")
    dateCreated: datetime = Field(..., description="Date when the study record was created")
    dateModified: datetime = Field(..., description="Last modification date of the study record")
