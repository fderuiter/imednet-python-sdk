"""Visit-related data models."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class VisitModel(BaseModel):
    """Model representing a subject visit instance in the iMednet system."""

    visitId: int = Field(..., description="Unique system identifier for the subject visit instance")
    studyKey: str = Field(..., description="Unique study key for the given study")
    intervalId: int = Field(..., description="Unique system identifier for the related interval")
    intervalName: str = Field(..., description="User-defined identifier for the related interval")
    subjectId: int = Field(..., description="Mednet Subject ID")
    subjectKey: str = Field(..., description="Protocol-assigned subject identifier")
    startDate: Optional[date] = Field(
        None, description="Subject visit Start Date defined in interval visit window"
    )
    endDate: Optional[date] = Field(
        None, description="Subject visit End Date defined in interval visit window"
    )
    dueDate: Optional[date] = Field(
        None, description="Subject visit Due Date defined in interval visit window"
    )
    visitDate: Optional[date] = Field(
        None, description="Subject visit Actual Date defined in interval visit window"
    )
    visitDateForm: Optional[str] = Field(
        None, description="Actual Date Form defined in interval visit window"
    )
    visitDateQuestion: Optional[str] = Field(None, description="User-defined field identifier")
    deleted: bool = Field(False, description="Subject visit deleted flag")
    dateCreated: datetime = Field(..., description="Date when this visit was created")
    dateModified: datetime = Field(..., description="Date when this visit was last modified")
