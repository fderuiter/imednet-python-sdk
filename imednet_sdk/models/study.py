"""Study-related data models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StudyModel(BaseModel):
    """Model representing a study in the iMednet system."""

    sponsorKey: str = Field(..., description="Sponsor key that this study belongs to")
    studyKey: str = Field(..., description="Unique study key")
    studyId: int = Field(..., description="Mednet study ID")
    studyName: str = Field(..., description="Study name")
    studyDescription: Optional[str] = Field(None, description="Detailed description of the study")
    studyType: str = Field(..., description="Type of the study")
    dateCreated: datetime = Field(..., description="Date when the study record was created")
    dateModified: datetime = Field(..., description="Last modification date of the study record")
