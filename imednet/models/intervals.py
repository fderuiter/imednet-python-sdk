from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .validators import (
    parse_bool,
    parse_datetime,
    parse_int_or_default,
    parse_list_or_default,
    parse_str_or_default,
)


class FormSummary(BaseModel):
    form_id: int = Field(0, alias="formId")
    form_key: str = Field("", alias="formKey")
    form_name: str = Field("", alias="formName")

    # allow instantiation via field names as well as aliases
    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> FormSummary:
        """
        Create a FormSummary instance from JSON-like dict.
        """
        return cls.model_validate(data)

    @field_validator("form_key", "form_name", mode="before")
    def _fill_strs(cls, v):
        return parse_str_or_default(v)

    @field_validator("form_id", mode="before")
    def _fill_ints(cls, v):
        return parse_int_or_default(v)


class Interval(BaseModel):
    """A class representing an interval in a study timeline.
    This class models various aspects of a study interval, including its identification,
    temporal properties, and associated forms.
    Attributes:
        study_key (str): The unique identifier for the study.
        interval_id (int): Unique identifier for the interval.
        interval_name (str): Name of the interval.
        interval_description (str): Description of the interval.
        interval_sequence (int): The sequence number of the interval.
        interval_group_id (int): ID of the group this interval belongs to.
        interval_group_name (str): Name of the interval group.
        disabled (bool): Flag indicating if the interval is disabled.
        date_created (datetime): Timestamp of interval creation.
        date_modified (datetime): Timestamp of last modification.
        timeline (str): Timeline identifier for the interval.
        defined_using_interval (str): Reference to interval used for definition.
        window_calculation_form (str): Form used for window calculations.
        window_calculation_date (str): Date used for window calculations.
        actual_date_form (str): Form containing actual date information.
        actual_date (str): The actual date of the interval.
        due_date_will_be_in (int): Number of days until due date.
        negative_slack (int): Allowed negative slack in days.
        positive_slack (int): Allowed positive slack in days.
        epro_grace_period (int): Grace period for ePRO in days.
        forms (List[FormSummary]): List of forms associated with this interval.
    Methods:
        from_json(data: Dict[str, Any]) -> Interval:
            Creates an Interval instance from a JSON-like dictionary."""

    study_key: str = Field("", alias="studyKey")
    interval_id: int = Field(0, alias="intervalId")
    interval_name: str = Field("", alias="intervalName")
    interval_description: str = Field("", alias="intervalDescription")
    interval_sequence: int = Field(0, alias="intervalSequence")
    interval_group_id: int = Field(0, alias="intervalGroupId")
    interval_group_name: str = Field("", alias="intervalGroupName")
    disabled: bool = Field(False, alias="disabled")
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_modified: datetime = Field(default_factory=datetime.now, alias="dateModified")
    timeline: str = Field("", alias="timeline")
    defined_using_interval: str = Field("", alias="definedUsingInterval")
    window_calculation_form: str = Field("", alias="windowCalculationForm")
    window_calculation_date: str = Field("", alias="windowCalculationDate")
    actual_date_form: str = Field("", alias="actualDateForm")
    actual_date: str = Field("", alias="actualDate")
    due_date_will_be_in: int = Field(0, alias="dueDateWillBeIn")
    negative_slack: int = Field(0, alias="negativeSlack")
    positive_slack: int = Field(0, alias="positiveSlack")
    epro_grace_period: int = Field(0, alias="eproGracePeriod")
    forms: List[FormSummary] = Field(default_factory=list, alias="forms")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator(
        "study_key",
        "interval_name",
        "interval_description",
        "interval_group_name",
        "timeline",
        "defined_using_interval",
        "window_calculation_form",
        "window_calculation_date",
        "actual_date_form",
        "actual_date",
        mode="before",
    )
    def _fill_strs(cls, v):
        return parse_str_or_default(v)

    @field_validator(
        "interval_id",
        "interval_sequence",
        "interval_group_id",
        "due_date_will_be_in",
        "negative_slack",
        "positive_slack",
        "epro_grace_period",
        mode="before",
    )
    def _fill_ints(cls, v):
        return parse_int_or_default(v)

    @field_validator("forms", mode="before")
    def _fill_list(cls, v):
        return parse_list_or_default(v)

    @field_validator("date_created", "date_modified", mode="before")
    def _parse_datetimes(cls, v: str | datetime) -> datetime:
        return parse_datetime(v)

    @field_validator("disabled", mode="before")
    def parse_bool_field(cls, v: Any) -> bool:
        return parse_bool(v)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Interval:
        """
        Create an Interval instance from JSON-like dict, including nested forms.
        """
        return cls.model_validate(data)
