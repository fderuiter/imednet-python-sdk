"""Record revision-related data models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RecordRevisionModel(BaseModel):
    """Model representing a distinct state or version in the lifecycle of a record."""

    studyKey: str = Field(..., description="Unique study key for the given study")
    recordRevisionId: int = Field(
        ..., description="Unique system identifier for the record revision"
    )
    recordId: int = Field(..., description="Unique system identifier for the related record")
    recordOid: str = Field(..., description="Client-assigned record OID")
    recordRevision: int = Field(..., description="Record revision number")
    dataRevision: int = Field(..., description="Data revision number")
    recordStatus: str = Field(..., description="User-defined record status")
    subjectId: int = Field(..., description="Mednet Subject ID")
    subjectOid: str = Field(..., description="Client-assigned subject OID")
    subjectKey: str = Field(..., description="Protocol-assigned subject identifier")
    siteId: int = Field(..., description="Unique system identifier for the related site")
    formKey: str = Field(..., description="Form key")
    intervalId: int = Field(..., description="Unique system identifier for the interval")
    role: str = Field(..., description="Role of the user who saved the record revision")
    user: str = Field(..., description="Username of the user who saved the record revision")
    reasonForChange: Optional[str] = Field(
        None, description="Reason for the change made in the record revision"
    )
    deleted: bool = Field(False, description="Indicates whether the record was deleted")
    dateCreated: datetime = Field(..., description="Date when the record revision was created")
