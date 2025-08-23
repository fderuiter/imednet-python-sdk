from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

from faker import Faker

from imednet.testing.logic_engine import LogicEngine
from imednet.testing.logic_parser import (
    BusinessRule,
    DisableAndClearField,
    HideAndClearField,
    LogicParser,
)
from imednet.workflows.record_update import RecordUpdateWorkflow

if TYPE_CHECKING:
    from imednet.models import Job
    from imednet.sdk import ImednetSDK
    from imednet.validation import DataDictionary


class RecordGenerator:
    """
    Generates and submits fake records based on a data dictionary.

    Args:
        sdk: An instance of the ImednetSDK.
        data_dictionary: An instance of the DataDictionary.
    """

    def __init__(self, sdk: ImednetSDK, data_dictionary: DataDictionary):
        self.sdk = sdk
        self.data_dictionary = data_dictionary
        self.faker = Faker()
        self.forms: Dict[str, dict] = {
            form["Form Key"]: form for form in data_dictionary.forms
        }
        self.questions: Dict[str, List[Dict[str, str]]] = {}
        for question in data_dictionary.questions:
            self.questions.setdefault(question["Form"], []).append(question)
        self.choices: Dict[Tuple[str, str], List[Dict[str, str]]] = {}
        for choice in data_dictionary.choices:
            self.choices.setdefault((choice["Form"], choice["Variable Name"]), []).append(choice)

        self.business_rules: Dict[str, List[BusinessRule]] = {}
        parser = LogicParser()
        for rule in data_dictionary.business_logic:
            logic = rule.get("Logic")
            if logic:
                parsed_rule = parser.parse(logic)
                self.business_rules.setdefault(rule["Form"], []).append(parsed_rule)

    def generate_and_submit_form(
        self,
        form_key: str,
        study_key: str,
        subject_identifier: str,
        wait_for_completion: bool = False,
    ) -> Job:
        """
        Generates and submits a new record for a given form.

        Args:
            form_key: The key of the form to generate data for.
            study_key: The key of the study to submit the record to.
            subject_identifier: The key of the subject to submit the record for.
            wait_for_completion: If True, wait for the submission job to complete.

        Returns:
            The job object for the submission.
        """
        record_data = self.generate_form_data(form_key)
        workflow = RecordUpdateWorkflow(self.sdk)

        return workflow.create_new_record(
            study_key=study_key,
            form_identifier=form_key,
            subject_identifier=subject_identifier,
            data=record_data,
            wait_for_completion=wait_for_completion,
        )

    def generate_form_data(self, form_key: str) -> dict[str, Any]:
        """
        Generates a dictionary of fake data for a given form, applying business logic.

        Args:
            form_key: The key of the form to generate data for.

        Returns:
            A dictionary of fake data, where keys are variable names and values are
            the generated data.
        """
        if form_key not in self.forms:
            raise ValueError(f"Form with key '{form_key}' not found in data dictionary.")

        form_questions = self.questions.get(form_key, [])
        if not form_questions:
            return {}

        # First pass: generate random data for all questions
        record_data = {}
        for question in form_questions:
            variable_name = question["Variable Name"]
            value = self._generate_value_for_question(question)
            if value is not None:
                record_data[variable_name] = value

        # Second pass: apply business logic to refine the data
        record_data = self._apply_business_logic(form_key, record_data)

        return record_data

    def _apply_business_logic(self, form_key: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """Applies business logic to a dictionary of record data."""
        form_rules = self.business_rules.get(form_key, [])
        if not form_rules:
            return record_data

        engine = LogicEngine(form_rules)
        actions = engine.evaluate(record_data)

        for action in actions:
            if isinstance(action, (DisableAndClearField, HideAndClearField)):
                if action.question in record_data:
                    del record_data[action.question]

        return record_data

    def _generate_value_for_question(self, question: dict[str, str]) -> Any:
        """Generate a single value for a given question."""
        variable_type = question["Variable Type"]

        # A simple dispatcher to generate data based on variable type
        if variable_type == "Radio":
            return self._generate_radio(question)
        if variable_type == "Date/Time":
            return self._generate_datetime(question)
        if variable_type == "Date/Time Precision":
            return self._generate_date(question)
        if variable_type == "Text":
            return self._generate_text(question)
        if variable_type == "Memo":
            return self._generate_memo(question)
        if variable_type == "Numeric":
            return self._generate_numeric(question)
        if variable_type == "Checkbox":
            return self._generate_checkbox(question)
        if variable_type == "File Upload":
            return self._generate_file_upload(question)
        if variable_type == "DICOM Upload":
            return self._generate_dicom_upload(question)

        # Fallback for unknown types, can be extended
        return None

    def _generate_radio(self, question: dict[str, str]) -> str | None:
        """Generate a value for a radio button question."""
        choices = self.choices.get((question["Form"], question["Variable Name"]))
        if not choices:
            return None
        return random.choice(choices)["Choice Value"]

    def _generate_datetime(self, question: dict[str, str]) -> str:
        """Generate a datetime string."""
        return self.faker.iso8601()

    def _generate_date(self, question: dict[str, str]) -> str:
        """Generate a date string."""
        return self.faker.date()

    def _generate_text(self, question: dict[str, str]) -> str:
        """Generate a short text."""
        return self.faker.sentence()

    def _generate_memo(self, question: dict[str, str]) -> str:
        """Generate a longer text for memo fields."""
        return self.faker.paragraph()

    def _generate_numeric(self, question: dict[str, str]) -> int:
        """Generate a numeric value."""
        return self.faker.random_int(min=0, max=100)

    def _generate_checkbox(self, question: dict[str, str]) -> str:
        """Generate a value for a checkbox question."""
        # Checkboxes often have "1" for checked and "0" for unchecked.
        return random.choice(["0", "1"])

    def _generate_file_upload(self, question: dict[str, str]) -> str:
        """Generate a fake file name for file uploads."""
        return self.faker.file_name(extension="pdf")

    def _generate_dicom_upload(self, question: dict[str, str]) -> str:
        """Generate a fake file name for DICOM uploads."""
        return self.faker.file_name(extension="dcm")
