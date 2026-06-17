from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class FormSummary(JsonModel):
    """Minimal form details embedded within an interval definition."""

    form_id: int = Field(0, alias="formId")
    form_key: str = Field("", alias="formKey")
    form_name: str = Field("", alias="formName")

    pass


class Interval(JsonModel):
    """Represents a visit interval or event within the study timeline."""

    interval_id: Optional[str] = Field(None, alias="intervalId")
    interval_name: Optional[str] = Field(None, alias="intervalName")
    disabled: Optional[bool] = Field(None, alias="disabled")
    forms: Optional[List[FormSummary]] = None
    timeline: Optional[str] = None
    defined_using_interval: Optional[str] = Field(None, alias="definedUsingInterval")
    window_calculation_form: Optional[str] = Field(None, alias="windowCalculationForm")
    window_calculation_date: Optional[str] = Field(None, alias="windowCalculationDate")
    actual_date_form: Optional[str] = Field(None, alias="actualDateForm")
    actual_date: Optional[str] = Field(None, alias="actualDate")
    due_date_will_be_in: Optional[int] = Field(None, alias="dueDateWillBeIn")
    negative_slack: Optional[int] = Field(None, alias="negativeSlack")
    positive_slack: Optional[int] = Field(None, alias="positiveSlack")
    epro_grace_period: Optional[int] = Field(None, alias="eproGracePeriod")


Interval = ModelEngine.get_model('Interval', Interval)
