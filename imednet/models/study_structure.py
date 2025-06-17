from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

# Import existing models needed for type hints and potentially reuse
from .forms import Form
from .intervals import Interval
from .variables import Variable


# Define a structure for Forms within the context of an Interval, including variables
class FormStructure(BaseModel):
    # Key identifying fields
    form_id: int = Field(..., alias="formId")
    form_key: str = Field(..., alias="formKey")
    form_name: str = Field(..., alias="formName")

    # Additional relevant fields from Form
    form_type: str = Field(..., alias="formType")
    revision: int = Field(..., alias="revision")
    disabled: bool = Field(..., alias="disabled")
    epro_form: bool = Field(..., alias="eproForm")
    allow_copy: bool = Field(..., alias="allowCopy")
    date_created: datetime = Field(..., alias="dateCreated")
    date_modified: datetime = Field(..., alias="dateModified")

    # Nested variables
    variables: List[Variable] = Field(default_factory=list)

    # Use ConfigDict for model configuration
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    @classmethod
    def from_form(cls, form: Form, variables: List[Variable]) -> FormStructure:
        """Creates FormStructure from a Form model and its associated variables."""
        form_data = form.model_dump(by_alias=True)
        return cls(**form_data, variables=variables)


# Define a structure for Intervals, containing FormStructures
class IntervalStructure(BaseModel):
    # Key identifying fields
    interval_id: int = Field(..., alias="intervalId")
    interval_name: str = Field(..., alias="intervalName")

    # Additional relevant fields from Interval
    interval_sequence: int = Field(..., alias="intervalSequence")
    interval_description: str = Field(..., alias="intervalDescription")
    interval_group_name: str = Field(..., alias="intervalGroupName")
    disabled: bool = Field(..., alias="disabled")
    date_created: datetime = Field(..., alias="dateCreated")
    date_modified: datetime = Field(..., alias="dateModified")

    # Nested forms
    forms: List[FormStructure] = Field(default_factory=list)

    # Use ConfigDict for model configuration
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    @classmethod
    def from_interval(cls, interval: Interval, forms: List[FormStructure]) -> IntervalStructure:
        """Creates IntervalStructure from an Interval model and its associated FormStructures."""
        interval_data = interval.model_dump(by_alias=True)
        # Remove the 'forms' key to avoid multiple values for keyword argument 'forms'
        interval_data.pop("forms", None)
        return cls(**interval_data, forms=forms)


# Define the root StudyStructure model
class StudyStructure(BaseModel):
    study_key: str = Field(..., alias="studyKey")
    intervals: List[IntervalStructure] = Field(default_factory=list)

    # Use ConfigDict for model configuration
    model_config = ConfigDict(populate_by_name=True)
