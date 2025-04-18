"""Subject-related data models."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class KeywordModel(BaseModel):
    """Model representing a keyword associated with a subject."""

    keywordName: str = Field(..., description="Name of the keyword")
    keywordKey: str = Field(..., description="Unique key for the keyword")
    keywordId: int = Field(..., description="Unique ID for the keyword")
    dateAdded: datetime = Field(..., description="Date when the keyword was added")


class SubjectModel(BaseModel):
    """Model representing a subject in the iMednet system."""

    studyKey: str = Field(..., description="Unique study key for the given study")
    subjectId: int = Field(..., description="Mednet Subject ID")
    subjectOid: str = Field(..., description="Client-assigned subject OID")
    subjectKey: str = Field(..., description="Protocol-assigned subject identifier")
    subjectStatus: str = Field(..., description="Current status of the subject")
    siteId: int = Field(..., description="Mednet Site ID")
    siteName: str = Field(..., description="Name of the site")
    enrollmentStartDate: datetime = Field(
        ..., description="Date when the subject enrollment started"
    )
    deleted: bool = Field(False, description="Indicates whether the subject was deleted")
    dateCreated: datetime = Field(..., description="Date when the subject record was created")
    dateModified: datetime = Field(..., description="Last modification date of the subject record")
    keywords: Optional[List[KeywordModel]] = Field(
        default=None, description="List of keywords associated with the subject"
    )
