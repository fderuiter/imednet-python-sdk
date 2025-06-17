import asyncio
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
    """Fetches and aggregates study structure information (intervals, forms, variables).

    Args:
        sdk: An initialized ImednetSDK instance.
        study_key: The key of the study to fetch structure for.

    Returns:
        A StudyStructure object containing nested intervals, forms, and variables.

    Raises:
        ImednetError: If fetching any part of the structure fails.
    """
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
            for form_summary in interval.forms:
                full_form = forms_by_id.get(form_summary.form_id)
                if full_form:
                    form_vars = variables_by_form_id.get(full_form.form_id, [])
                    form_structures.append(FormStructure.from_form(full_form, form_vars))

            interval_structures.append(IntervalStructure.from_interval(interval, form_structures))

        return StudyStructure(study_key=study_key, intervals=interval_structures)  # type: ignore[call-arg]

    except Exception as e:
        # Catch potential API errors or processing errors
        raise ImednetError(
            f"Failed to retrieve or process study structure for {study_key}: {e}"
        ) from e


async def async_get_study_structure(sdk: "ImednetSDK", study_key: str) -> StudyStructure:
    """Asynchronous variant of :func:`get_study_structure`."""
    try:
        intervals, forms, variables = await asyncio.gather(
            sdk.intervals.async_list(study_key),
            sdk.forms.async_list(study_key),
            sdk.variables.async_list(study_key),
        )

        forms_by_id: Dict[int, Form] = {f.form_id: f for f in forms}
        variables_by_form_id: Dict[int, List[Variable]] = {}
        for var in variables:
            variables_by_form_id.setdefault(var.form_id, []).append(var)

        interval_structures: List[IntervalStructure] = []
        for interval in intervals:
            form_structures: List[FormStructure] = []
            for form_summary in interval.forms:
                full_form = forms_by_id.get(form_summary.form_id)
                if full_form:
                    form_vars = variables_by_form_id.get(full_form.form_id, [])
                    form_structures.append(FormStructure.from_form(full_form, form_vars))

            interval_structures.append(IntervalStructure.from_interval(interval, form_structures))

        return StudyStructure(
            study_key=study_key, intervals=interval_structures
        )  # type: ignore[call-arg]

    except Exception as e:  # pragma: no cover - unexpected
        raise ImednetError(
            f"Failed to retrieve or process study structure for {study_key}: {e}"
        ) from e
