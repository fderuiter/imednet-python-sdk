"""Pydantic models related to iMednet Intervals (Visits).

This module defines the Pydantic models `IntervalFormModel` and `IntervalModel`
which represent the structure of interval/visit definition data retrieved from
the iMednet API, typically via the `/intervals` endpoint.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class IntervalFormModel(BaseModel):
    """Represents a simplified view of a form associated with an interval.

    Used within the `IntervalModel` to list the forms expected during that interval.

    Attributes:
        formId: Unique numeric identifier for the form definition.
        formKey: Unique string identifier for the form definition.
        formName: The display name of the eCRF.
    """

    formId: int = Field(..., description="Form ID")
    formKey: str = Field(..., description="Form Key")
    formName: str = Field(..., description="Form Name")


class IntervalModel(BaseModel):
    """Represents the definition of an Interval (often synonymous with Visit) in iMednet.

    This model captures metadata about an interval, including its identifiers, name,
description, sequence, scheduling rules, and associated forms.

    Attributes:
        studyKey: Unique identifier for the study this interval belongs to.
        intervalId: Unique numeric identifier assigned by iMednet to the interval definition.
        intervalName: User-defined name for the interval/visit.
        intervalDescription: Optional user-defined description for the interval/visit.
        intervalSequence: User-defined sequence number for ordering intervals.
        intervalGroupId: User-defined numeric identifier for the interval group.
        intervalGroupName: User-defined name for the interval group.
        timeline: The type of visit window calculation (e.g., "Static", "Dynamic").
        definedUsingInterval: Optional name of the baseline interval used for date calculations
                              if `timeline` is dynamic.
        windowCalculationForm: Optional key of the baseline form used for date calculations
                               if `timeline` is dynamic.
        windowCalculationDate: Optional name of the baseline date field used for calculations
                               if `timeline` is dynamic.
        actualDateForm: Optional key of the form containing the actual date field for this interval.
        actualDate: Optional name of the field containing the actual date for this interval.
        dueDateWillBeIn: Optional number of days from the baseline date when this interval is due.
        negativeSlack: Optional allowed number of days *before* the due date the interval can occur.
        positiveSlack: Optional allowed number of days *after* the due date the interval can occur.
        eproGracePeriod: Optional allowed number of additional days for ePRO completion after the due date.
        forms: A list of `IntervalFormModel` objects representing the forms associated with this interval.
        disabled: Boolean flag indicating if the interval is currently disabled (soft delete).
        dateCreated: The date and time when the interval definition was initially created.
        dateModified: The date and time when the interval definition was last modified.
    """

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
