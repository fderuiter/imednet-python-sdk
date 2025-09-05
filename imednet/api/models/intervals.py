from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import Field

from .json_base import JsonModel


class FormSummary(JsonModel):
    """A brief summary of a form, typically used in lists."""

    form_id: int = Field(0, alias="formId", description="The ID of the form.")
    form_key: str = Field("", alias="formKey", description="The key of the form.")
    form_name: str = Field("", alias="formName", description="The name of the form.")


class Interval(JsonModel):
    """Represents a visit interval in a study's schedule."""

    study_key: str = Field("", alias="studyKey", description="The key of the study.")
    interval_id: int = Field(0, alias="intervalId", description="The ID of the interval.")
    interval_name: str = Field("", alias="intervalName", description="The name of the interval.")
    interval_description: str = Field(
        "", alias="intervalDescription", description="The description of the interval."
    )
    interval_sequence: int = Field(
        0, alias="intervalSequence", description="The sequence number of the interval."
    )
    interval_group_id: int = Field(
        0, alias="intervalGroupId", description="The ID of the interval group."
    )
    interval_group_name: str = Field(
        "", alias="intervalGroupName", description="The name of the interval group."
    )
    disabled: bool = Field(
        False, alias="disabled", description="Indicates if the interval is disabled."
    )
    date_created: datetime = Field(
        default_factory=datetime.now,
        alias="dateCreated",
        description="The date the interval was created.",
    )
    date_modified: datetime = Field(
        default_factory=datetime.now,
        alias="dateModified",
        description="The date the interval was last modified.",
    )
    timeline: str = Field("", alias="timeline", description="The timeline of the interval.")
    defined_using_interval: str = Field(
        "", alias="definedUsingInterval", description="The interval used to define this interval."
    )
    window_calculation_form: str = Field(
        "", alias="windowCalculationForm", description="The form used for window calculation."
    )
    window_calculation_date: str = Field(
        "", alias="windowCalculationDate", description="The date used for window calculation."
    )
    actual_date_form: str = Field(
        "", alias="actualDateForm", description="The form used for the actual date."
    )
    actual_date: str = Field("", alias="actualDate", description="The actual date.")
    due_date_will_be_in: int = Field(
        0, alias="dueDateWillBeIn", description="The number of days until the due date."
    )
    negative_slack: int = Field(0, alias="negativeSlack", description="The negative slack in days.")
    positive_slack: int = Field(0, alias="positiveSlack", description="The positive slack in days.")
    epro_grace_period: int = Field(
        0, alias="eproGracePeriod", description="The ePRO grace period in days."
    )
    forms: List[FormSummary] = Field(
        default_factory=list, alias="forms", description="The forms associated with this interval."
    )
