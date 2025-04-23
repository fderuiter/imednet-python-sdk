import datetime
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class FormSummary:
    form_id: int
    form_key: str
    form_name: str

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "FormSummary":
        """
        Create a FormSummary instance from JSON data.

        Args:
            data: Dictionary containing form summary data from the API

        Returns:
            FormSummary instance with the data
        """
        return cls(
            form_id=data.get("formId", 0),
            form_key=data.get("formKey", ""),
            form_name=data.get("formName", ""),
        )


@dataclass
class Interval:
    study_key: str
    interval_id: int
    interval_name: str
    interval_description: str
    interval_sequence: int
    interval_group_id: int
    interval_group_name: str
    disabled: bool
    date_created: datetime.datetime
    date_modified: datetime.datetime
    timeline: str
    defined_using_interval: str
    window_calculation_form: str
    window_calculation_date: str
    actual_date_form: str
    actual_date: str
    due_date_will_be_in: int
    negative_slack: int
    positive_slack: int
    epro_grace_period: int
    forms: List[FormSummary]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Interval":
        """
        Create an Interval instance from JSON data.

        Args:
            data: Dictionary containing interval data from the API

        Returns:
            Interval instance with the data
        """
        # Parse datetime strings
        date_created = (
            datetime.datetime.fromisoformat(data.get("dateCreated", "").replace(" ", "T"))
            if data.get("dateCreated")
            else datetime.datetime.now()
        )

        date_modified = (
            datetime.datetime.fromisoformat(data.get("dateModified", "").replace(" ", "T"))
            if data.get("dateModified")
            else datetime.datetime.now()
        )

        # Handle nested forms
        forms = []
        forms_data = data.get("forms", [])
        for form_data in forms_data:
            forms.append(FormSummary.from_json(form_data))

        return cls(
            study_key=data.get("studyKey", ""),
            interval_id=data.get("intervalId", 0),
            interval_name=data.get("intervalName", ""),
            interval_description=data.get("intervalDescription", ""),
            interval_sequence=data.get("intervalSequence", 0),
            interval_group_id=data.get("intervalGroupId", 0),
            interval_group_name=data.get("intervalGroupName", ""),
            disabled=data.get("disabled", False),
            date_created=date_created,
            date_modified=date_modified,
            timeline=data.get("timeline", ""),
            defined_using_interval=data.get("definedUsingInterval", ""),
            window_calculation_form=data.get("windowCalculationForm", ""),
            window_calculation_date=data.get("windowCalculationDate", ""),
            actual_date_form=data.get("actualDateForm", ""),
            actual_date=data.get("actualDate", ""),
            due_date_will_be_in=data.get("dueDateWillBeIn", 0),
            negative_slack=data.get("negativeSlack", 0),
            positive_slack=data.get("positiveSlack", 0),
            epro_grace_period=data.get("eproGracePeriod", 0),
            forms=forms,
        )
