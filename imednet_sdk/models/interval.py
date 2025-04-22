"""Pydantic models related to iMednet Intervals (Visits).

This module defines the Pydantic models `IntervalFormModel` and `IntervalModel`
which represent the structure of interval/visit definition data retrieved from
the iMednet API, typically via the `/intervals` endpoint.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    """Represents the definition of an Interval (often synonymous with Visit) in iMednet."""

    # --- Core Required Fields (Based on typical API usage & potential test failures) ---
    # Assuming these are generally required for a valid interval definition
    studyKey: str = Field(..., description="Unique study key")
    intervalId: int = Field(..., description="Unique system identifier for the interval definition")
    # Ensure intervalName is required as per test failure
    intervalName: str = Field(..., description="User-defined interval/visit name")
    intervalSequence: int = Field(..., description="User-defined sequence of the interval")
    intervalGroupId: int = Field(..., description="User-defined interval group ID")
    intervalGroupName: str = Field(..., description="User-defined interval group name")
    timeline: str = Field(
        ..., description="Type of Interval Visit Window (e.g., 'Static', 'Dynamic')"
    )
    forms: List[IntervalFormModel] = Field(
        default_factory=list, description="List of forms associated with the interval"
    )
    disabled: bool = Field(
        False, description="Indicates if the interval definition is disabled (soft delete)"
    )
    dateCreated: datetime = Field(..., description="Date when the interval definition was created")
    dateModified: datetime = Field(
        ..., description="Last modification date of the interval definition"
    )

    # --- Optional Fields (Based on API docs/structure) ---
    intervalDescription: Optional[str] = Field(
        None, description="User-defined interval/visit description"
    )
    # Optional scheduling fields
    definedUsingInterval: Optional[str] = Field(
        None, description="Baseline interval name used for date calculations"
    )
    windowCalculationForm: Optional[str] = Field(
        None, description="Baseline form key used for date calculations"
    )
    windowCalculationDate: Optional[str] = Field(
        None, description="Baseline variable name used for date calculations"
    )
    actualDateForm: Optional[str] = Field(
        None, description="Form key containing the actual date field for this interval"
    )
    actualDate: Optional[str] = Field(
        None, description="Variable name of the actual date field for this interval"
    )
    dueDateWillBeIn: Optional[int] = Field(
        None, description="Number of days from the baseline date the interval is due"
    )
    negativeSlack: Optional[int] = Field(
        None, description="Allowed number of days before the due date the interval can occur"
    )
    positiveSlack: Optional[int] = Field(
        None, description="Allowed number of days after the due date the interval can occur"
    )
    eproGracePeriod: Optional[int] = Field(
        None, description="Allowed number of additional days for ePRO completion after the due date"
    )

    # --- Removed Redundant/Conflicting Optional Definitions ---
    # Removed the block of Optional[...] fields that duplicated required ones like intervalId, intervalName etc.
    # Keep only truly optional fields or fields whose presence might vary.

    # --- Additional Optional Fields (From original model, verify necessity) ---
    # These might be useful but were potentially part of the duplication. Keep if needed.
    intervalKey: Optional[str] = Field(
        None, description="A unique key identifying the interval, often user-defined."
    )
    intervalOrder: Optional[int] = Field(  # Potentially redundant with intervalSequence
        None, description="The sequential order of the interval within the study schedule."
    )
    intervalIsRepeating: Optional[bool] = Field(
        None, description="Indicates if this interval can occur multiple times for a subject."
    )
    intervalIsUnscheduled: Optional[bool] = Field(
        None, description="Indicates if this interval is not part of the regular schedule."
    )
    # intervalIsArchived might be redundant with 'disabled' flag, clarify API meaning
    intervalIsArchived: Optional[bool] = Field(
        None, description="Indicates if the interval definition is archived."
    )
    # Timestamps might be redundant with dateCreated/dateModified, clarify API meaning
    intervalDateCreated: Optional[datetime] = Field(
        None,
        description="The date and time when the interval definition was created (potentially redundant).",
    )
    intervalDateUpdated: Optional[datetime] = Field(
        None,
        description="The date and time when the interval definition was last updated (potentially redundant).",
    )
    intervalUpdatedByUserName: Optional[str] = Field(
        None, description="The username of the user who last updated the interval definition."
    )
    intervalCreatedByUserName: Optional[str] = Field(
        None, description="The username of the user who created the interval definition."
    )

    # Allow extra fields if the API might add more properties
    model_config = ConfigDict(extra="allow", populate_by_name=True)  # Added populate_by_name

    # Keep validator if date formats need parsing
    @field_validator(
        "dateCreated", "dateModified", "intervalDateCreated", "intervalDateUpdated", mode="before"
    )
    @classmethod
    def parse_datetime_optional(cls, value):
        """Parse datetime strings into datetime objects, handling None."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        # Basic ISO format parsing, adjust if API uses different formats
        try:
            # Handle potential 'Z' for UTC
            if "Z" in str(value):
                value = str(value).replace("Z", "+00:00")
            return datetime.fromisoformat(str(value))
        except Exception as e:
            raise ValueError(f"Invalid datetime format for value: {value}") from e
