"""Retrieve the hierarchical structure of a study in iMednet."""

from typing import TYPE_CHECKING, Dict, List

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

# Use TYPE_CHECKING to avoid circular import at runtime
if TYPE_CHECKING:
    from imednet.sdk import ImednetSDK


def get_study_structure(sdk: "ImednetSDK", study_key: str) -> StudyStructure:
    """Return the intervals, forms and variables comprising a study."""
    try:
        # Fetch all components concurrently (if async were used) or sequentially
        intervals: List[Interval] = sdk.intervals.list(study_key)
        forms: List[Form] = sdk.forms.list(study_key)
        variables: List[Variable] = sdk.variables.list(study_key)

        # Organize data for efficient lookup
        forms_by_id: Dict[int, Form] = {f.form_id: f for f in forms}
        variables_by_form_id: Dict[int, List[Variable]] = {}
        for var in variables:
            variables_by_form_id.setdefault(var.form_id, []).append(var)

        # Build the nested structure
        interval_structures: List[IntervalStructure] = []
        for interval in intervals:
            form_structures: List[FormStructure] = []
            # Assuming interval.forms contains summaries or just IDs/Keys
            # We need to look up the full Form object and its variables
            for form_summary in interval.forms:  # Assuming interval.forms exists
                full_form = forms_by_id.get(form_summary.form_id)
                if full_form:
                    form_vars = variables_by_form_id.get(full_form.form_id, [])
                    form_struct = FormStructure(
                        **full_form.model_dump(),  # Pass Form fields
                        variables=form_vars,  # Add fetched variables
                    )
                    form_structures.append(form_struct)

            interval_struct = IntervalStructure(
                **interval.model_dump(),  # Pass Interval fields
                forms=form_structures,  # Add nested FormStructures
            )
            interval_structures.append(interval_struct)

        return StudyStructure(study_key=study_key, intervals=interval_structures)  # type: ignore[call-arg]

    except Exception as e:
        # Catch potential API errors or processing errors
        raise ImednetError(
            f"Failed to retrieve or process study structure for {study_key}: {e}"
        ) from e
