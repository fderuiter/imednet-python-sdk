"""Pydantic models related to iMednet Subjects.

This module defines the Pydantic models `KeywordModel` (reused from records, consider moving
to common if identical) and `SubjectModel` which represent the structure of subject information
retrieved from the iMednet API, typically via the `/subjects` endpoint.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class KeywordModel(BaseModel):
    """Represents a keyword associated with a subject in iMednet.

    Keywords can be used to tag or categorize subjects.
    (Note: This might be identical to the KeywordModel in record.py; consider consolidation).

    Attributes:
        keywordName: The name of the keyword.
        keywordKey: The unique key identifier for the keyword.
        keywordId: The unique numeric identifier for the keyword.
        dateAdded: The date and time when the keyword was associated with the subject.
    """

    keywordName: str = Field(..., description="Name of the keyword")
    keywordKey: str = Field(..., description="Unique key for the keyword")
    keywordId: int = Field(..., description="Unique ID for the keyword")
    dateAdded: datetime = Field(..., description="Date when the keyword was added")


class SubjectModel(BaseModel):
    """Represents a participant (subject) enrolled in a study in iMednet.

    This model captures key information about a subject, including their identifiers,
    status, site assignment, enrollment date, and associated keywords.

    Attributes:
        studyKey: Unique identifier for the study this subject is enrolled in.
        subjectId: Unique numeric identifier assigned by iMednet to this subject.
        subjectOid: Client-assigned Object Identifier (OID) for this subject.
        subjectKey: Protocol-assigned subject identifier (often the screen/randomization ID).
        subjectStatus: The current status of the subject within the study (e.g., "Enrolled",
                       "Screen Failed", "Completed", "Withdrawn").
        siteId: Unique numeric identifier for the site the subject is assigned to.
        siteName: The name of the site the subject is assigned to.
        enrollmentStartDate: The date and time when the subject's enrollment started.
        deleted: Boolean flag indicating if the subject record is marked as deleted.
        dateCreated: The date and time when the subject record was initially created.
        dateModified: The date and time when the subject record was last modified.
        keywords: An optional list of `KeywordModel` objects associated with the subject.
    """

    studyKey: str = Field(..., description="Unique study key for the given study")
    subjectId: int = Field(..., description="Mednet Subject ID")
    subjectOid: Optional[str] = Field(None, description="Client-assigned subject OID")
    subjectKey: str = Field(..., description="Protocol-assigned subject identifier")
    subjectStatus: str = Field(..., description="Current status of the subject")
    siteId: int = Field(..., description="Mednet Site ID")
    siteName: str = Field(..., description="Name of the site")
    enrollmentStartDate: Optional[datetime] = Field(
        None, description="Date when the subject enrollment started"
    )
    deleted: bool = Field(False, description="Indicates whether the subject was deleted")
    dateCreated: datetime = Field(..., description="Date when the subject record was created")
    dateModified: datetime = Field(..., description="Last modification date of the subject record")
    keywords: Optional[List[KeywordModel]] = Field(
        default=None, description="List of keywords associated with the subject"
    )
