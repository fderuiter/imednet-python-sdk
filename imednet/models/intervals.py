from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import Field

from imednet.models.json_base import JsonModel


class FormSummary(JsonModel):
    form_id: int = Field(0, alias="formId")
    form_key: str = Field("", alias="formKey")
    form_name: str = Field("", alias="formName")

    pass


class Interval(JsonModel):
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

    pass
