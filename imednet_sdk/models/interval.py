"""Interval-related data models."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class IntervalFormModel(BaseModel):
    """Model representing a form associated with an interval."""

    formId: int = Field(..., description="Form ID")
    formKey: str = Field(..., description="Form Key")
    formName: str = Field(..., description="Form Name")


class IntervalModel(BaseModel):
    """Model representing a design resource defining a set of forms and scheduling window."""

    studyKey: str = Field(..., description="Unique study key")
    intervalId: int = Field(..., description="Unique system identifier for the interval")
    intervalName: str = Field(..., description="User-defined interval/visit name")
    intervalDescription: Optional[str] = Field(
        None, description="User-defined interval/visit description"
    )
    intervalSequence: int = Field(..., description="User-defined sequence of the interval")
    intervalGroupId: int = Field(..., description="User-defined interval group ID")
    intervalGroupName: str = Field(..., description="User-defined interval group name")
    timeline: str = Field(..., description="Type of Interval Visit Window")
    definedUsingInterval: Optional[str] = Field(
        None, description="Baseline interval used for date calculations"
    )
    windowCalculationForm: Optional[str] = Field(
        None, description="Baseline form used for date calculations"
    )
    windowCalculationDate: Optional[str] = Field(
        None, description="Baseline field used for date calculations"
    )
    actualDateForm: Optional[str] = Field(
        None, description="Actual date form for a specific interval"
    )
    actualDate: Optional[str] = Field(None, description="Actual date field for a specific interval")
    dueDateWillBeIn: Optional[int] = Field(
        None, description="Number of days from the baseline date the interval is due"
    )
    negativeSlack: Optional[int] = Field(
        None, description="Allowed number of negative days from the due date"
    )
    positiveSlack: Optional[int] = Field(
        None, description="Allowed number of positive days from the due date"
    )
    eproGracePeriod: Optional[int] = Field(
        None, description="Allowed number of positive days for ePRO from the due date"
    )
    forms: List[IntervalFormModel] = Field(
        default_factory=list, description="List of forms associated with the interval"
    )
    disabled: bool = Field(False, description="Indicates if the interval is soft-deleted")
    dateCreated: datetime = Field(..., description="Date when the interval was created")
    dateModified: datetime = Field(..., description="Last modification date of the interval")
