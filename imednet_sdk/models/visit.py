"""Pydantic models related to iMednet Subject Visits.

This module defines the Pydantic model `VisitModel` which represents the
structure of subject visit instance data retrieved from the iMednet API,
typically via the `/visits` endpoint.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class VisitModel(BaseModel):
    """Represents a specific instance of a subject visit within a study schedule.

    This model captures details about a scheduled or actual visit for a subject,
    linking it to the subject, the planned interval, and relevant dates.

    Attributes:
        visitId: Unique numeric identifier assigned by iMednet to this specific visit instance.
        studyKey: Unique identifier for the study this visit belongs to.
        intervalId: Unique numeric identifier for the interval definition this visit corresponds to.
        intervalName: User-defined name of the interval definition.
        subjectId: Unique numeric identifier assigned by iMednet to the subject.
        subjectKey: Protocol-assigned subject identifier (often the screen/randomization ID).
        startDate: Optional calculated start date of the visit window.
        endDate: Optional calculated end date of the visit window.
        dueDate: Optional calculated due date for the visit.
        visitDate: Optional actual date the visit occurred, typically entered on a form.
        visitDateForm: Optional key of the form where the `visitDate` is recorded.
        visitDateQuestion: Optional name of the variable (field) where the `visitDate` is recorded.
        deleted: Boolean flag indicating if this visit instance is marked as deleted.
        dateCreated: The date and time when this visit instance record was created.
        dateModified: The date and time when this visit instance record was last modified.
    """

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
