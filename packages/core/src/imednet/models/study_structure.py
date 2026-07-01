"""Models for representing the hierarchical structure of a study."""

from __future__ import annotations

from datetime import datetime
from typing import List

from msgspec import Struct
from msgspec import field as Field

# Import existing models needed for type hints and potentially reuse
from .forms import Form
from .intervals import Interval
from .variables import Variable


# Define a structure for Forms within the context of an Interval, including variables
class FormStructure(Struct, kw_only=True, omit_defaults=True):
    """Hierarchical representation of a form including its variables."""

    # Key identifying fields
    form_id: int 
    form_key: str 
    form_name: str 

    # Additional relevant fields from Form
    form_type: str 
    revision: int 
    disabled: bool | None = Field(default=None)
    epro_form: bool 
    allow_copy: bool 
    date_created: datetime 
    date_modified: datetime 

    # Nested variables
    variables: List[Variable] = Field(default_factory=list)

    # Use ConfigDict for model configuration
    

    @classmethod
    def from_form(cls, form: Form, variables: List[Variable]) -> FormStructure:
        """Creates FormStructure from a Form model and its associated variables."""
        import msgspec
        form_data = msgspec.structs.asdict(form)
        return cls(**form_data, variables=variables)


# Define a structure for Intervals, containing FormStructures
class IntervalStructure(Struct, kw_only=True, omit_defaults=True):
    """Hierarchical representation of an interval including its forms."""

    # Key identifying fields
    interval_id: int 
    interval_name: str 

    # Additional relevant fields from Interval
    interval_sequence: int 
    interval_description: str 
    interval_group_name: str 
    disabled: bool | None = Field(default=None)
    date_created: datetime 
    date_modified: datetime 

    # Nested forms
    forms: List[FormStructure] = Field(default_factory=list)

    # Use ConfigDict for model configuration
    

    @classmethod
    def from_interval(cls, interval: Interval, forms: List[FormStructure]) -> IntervalStructure:
        """Creates IntervalStructure from an Interval model and its associated FormStructures."""
        import msgspec
        interval_data = msgspec.structs.asdict(interval)
        # Remove the 'forms' key to avoid multiple values for keyword argument 'forms'
        interval_data.pop("forms", None)
        return cls(**interval_data, forms=forms)


# Define the root StudyStructure model
class StudyStructure(Struct, kw_only=True, omit_defaults=True):
    """Hierarchical representation of a full study including intervals and forms."""

    study_key: str 
    intervals: List[IntervalStructure] = Field(default_factory=list)

    # Use ConfigDict for model configuration
    
