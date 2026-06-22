"""TODO: Add docstring."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from imednet.models.json_base import JsonModel


class FormSummary(JsonModel):
    """TODO: Add docstring."""

    form_id: Optional[int] = Field(default=None, alias="formId")
    form_key: Optional[str] = Field(default=None, alias="formKey")
    form_name: Optional[str] = Field(default=None, alias="formName")


    pass


class Interval(JsonModel):
    """TODO: Add docstring."""

    study_key: Optional[str] = Field(default=None, alias="studyKey")
    interval_id: Optional[int] = Field(default=None, alias="intervalId")
    interval_name: Optional[str] = Field(default=None, alias="intervalName")
    interval_description: Optional[str] = Field(default=None, alias="intervalDescription")
    interval_sequence: Optional[int] = Field(default=None, alias="intervalSequence")
    interval_group_id: Optional[int] = Field(default=None, alias="intervalGroupId")
    interval_group_name: Optional[str] = Field(default=None, alias="intervalGroupName")
    disabled: Optional[bool] = Field(default=None, alias="disabled")
    date_created: Optional[str] = Field(default=None, alias="dateCreated")
    date_modified: Optional[str] = Field(default=None, alias="dateModified")
    forms: List[FormSummary] = Field(default_factory=list, alias="forms")

