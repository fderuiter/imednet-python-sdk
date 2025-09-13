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
    """Represents the structure of a form, including its variables."""

    form_id: int = Field(..., alias="formId", description="The ID of the form.")
    form_key: str = Field(..., alias="formKey", description="The key of the form.")
    form_name: str = Field(..., alias="formName", description="The name of the form.")
    form_type: str = Field(..., alias="formType", description="The type of the form.")
    revision: int = Field(..., alias="revision", description="The revision number of the form.")
    disabled: bool = Field(..., alias="disabled", description="Indicates if the form is disabled.")
    epro_form: bool = Field(
        ..., alias="eproForm", description="Indicates if the form is an ePRO form."
    )
    allow_copy: bool = Field(
        ..., alias="allowCopy", description="Indicates if the form can be copied."
    )
    date_created: datetime = Field(
        ..., alias="dateCreated", description="The date the form was created."
    )
    date_modified: datetime = Field(
        ..., alias="dateModified", description="The date the form was last modified."
    )
    variables: List[Variable] = Field(
        default_factory=list, description="A list of variables within the form."
    )

    # Use ConfigDict for model configuration
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    @classmethod
    def from_form(cls, form: Form, variables: List[Variable]) -> FormStructure:
        """Create a FormStructure from a Form model and a list of variables.

        Args:
            form: The Form model instance.
            variables: The list of variables associated with the form.

        Returns:
            A new FormStructure instance.
        """
        form_data = form.model_dump(by_alias=True)
        return cls(**form_data, variables=variables)


# Define a structure for Intervals, containing FormStructures
class IntervalStructure(BaseModel):
    """Represents the structure of an interval, including its forms."""

    interval_id: int = Field(..., alias="intervalId", description="The ID of the interval.")
    interval_name: str = Field(..., alias="intervalName", description="The name of the interval.")
    interval_sequence: int = Field(
        ..., alias="intervalSequence", description="The sequence number of the interval."
    )
    interval_description: str = Field(
        ..., alias="intervalDescription", description="The description of the interval."
    )
    interval_group_name: str = Field(
        ..., alias="intervalGroupName", description="The name of the interval group."
    )
    disabled: bool = Field(
        ..., alias="disabled", description="Indicates if the interval is disabled."
    )
    date_created: datetime = Field(
        ..., alias="dateCreated", description="The date the interval was created."
    )
    date_modified: datetime = Field(
        ..., alias="dateModified", description="The date the interval was last modified."
    )
    forms: List[FormStructure] = Field(
        default_factory=list, description="A list of forms within the interval."
    )

    # Use ConfigDict for model configuration
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    @classmethod
    def from_interval(cls, interval: Interval, forms: List[FormStructure]) -> IntervalStructure:
        """Create an IntervalStructure from an Interval model and a list of form structures.

        Args:
            interval: The Interval model instance.
            forms: The list of form structures associated with the interval.

        Returns:
            A new IntervalStructure instance.
        """
        interval_data = interval.model_dump(by_alias=True)
        # Remove the 'forms' key to avoid multiple values for keyword argument 'forms'
        interval_data.pop("forms", None)
        return cls(**interval_data, forms=forms)


# Define the root StudyStructure model
class StudyStructure(BaseModel):
    """Represents the complete hierarchical structure of a study."""

    study_key: str = Field(..., alias="studyKey", description="The key of the study.")
    intervals: List[IntervalStructure] = Field(
        default_factory=list, description="A list of intervals within the study."
    )
    model_config = ConfigDict(populate_by_name=True)
