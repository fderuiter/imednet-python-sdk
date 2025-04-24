from typing import Dict, List

# Import potential exceptions
from imednet.core.exceptions import ImednetError

# Import the models we need
from imednet.models.forms import Form
from imednet.models.intervals import Interval
from imednet.models.study_structure import (
    FormStructure,
    IntervalStructure,
    StudyStructure,
)
from imednet.models.variables import Variable
from imednet.sdk import ImednetSDK


def get_study_structure(sdk: ImednetSDK, study_key: str) -> StudyStructure:
    """
    Fetches intervals, forms, and variables for a study and assembles them
    into a nested StudyStructure object.

    Args:
        sdk: An authenticated ImednetSDK instance.
        study_key: The key of the study to fetch the structure for.

    Returns:
        A StudyStructure object representing the study's hierarchy.

    Raises:
        ImednetError: If any API call fails.
    """
    try:
        all_intervals: List[Interval] = sdk.intervals.list(study_key=study_key)
        all_forms: List[Form] = sdk.forms.list(study_key=study_key)
        all_variables: List[Variable] = sdk.variables.list(study_key=study_key)
    except ImednetError as e:
        print(f"Error fetching data for study {study_key}: {e}")
        raise

    forms_by_id: Dict[int, Form] = {form.form_id: form for form in all_forms}
    variables_by_form_id: Dict[int, List[Variable]] = {}
    for var in all_variables:
        variables_by_form_id.setdefault(var.form_id, []).append(var)

    interval_structures: List[IntervalStructure] = []
    for interval in all_intervals:
        form_structures: List[FormStructure] = []
        for form_summary in interval.forms:
            full_form = forms_by_id.get(form_summary.form_id)
            if full_form:
                form_vars = variables_by_form_id.get(full_form.form_id, [])
                form_struct = FormStructure.from_form(full_form, form_vars)
                form_structures.append(form_struct)
        interval_struct = IntervalStructure.from_interval(interval, form_structures)
        interval_structures.append(interval_struct)

    study_structure = StudyStructure(studyKey=study_key, intervals=interval_structures)
    return study_structure
