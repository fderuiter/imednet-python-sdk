"""TODO: Add docstring."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from imednet.models.forms import Form
from imednet.models.intervals import FormSummary, Interval
from imednet.models.variables import Variable
from imednet_workflows.study_structure import async_get_study_structure, get_study_structure


@pytest.mark.parametrize("async_mode", [False, True])
def test_get_study_structure_aggregates_related_data(async_mode: bool) -> None:
    """TODO: Add docstring."""
    sdk = MagicMock()
    interval = Interval(
        interval_id=1,
        interval_name="INT1",
        interval_sequence=1,
        interval_description="desc",
        interval_group_name="grp",
        date_created="2024-01-01T00:00:00Z",
        date_modified="2024-01-01T00:00:00Z",
        forms=[FormSummary(form_id=1, form_key="F1", form_name="Form1")],
    )
    form = Form(
        form_id=1,
        form_key="F1",
        form_name="Form1",
        date_created="2024-01-01T00:00:00Z",
        date_modified="2024-01-01T00:00:00Z",
    )
    variable = Variable(variable_id=1, variable_name="V1", label="Var 1", form_id=1)

    if async_mode:

        async def async_mock_return(items):
            """TODO: Add docstring."""
            return items

        sdk.async_get_intervals = MagicMock(return_value=async_mock_return([interval]))
        sdk.async_get_forms = MagicMock(return_value=async_mock_return([form]))
        sdk.async_get_variables = MagicMock(return_value=async_mock_return([variable]))
        structure = asyncio.run(async_get_study_structure(sdk, "STUDY"))
        sdk.async_get_intervals.assert_called_once_with("STUDY")
        sdk.async_get_forms.assert_called_once_with("STUDY")
        sdk.async_get_variables.assert_called_once_with("STUDY")
    else:
        sdk.get_intervals.return_value = [interval]
        sdk.get_forms.return_value = [form]
        sdk.get_variables.return_value = [variable]
        structure = get_study_structure(sdk, "STUDY")
        sdk.get_intervals.assert_called_once_with("STUDY")
        sdk.get_forms.assert_called_once_with("STUDY")
        sdk.get_variables.assert_called_once_with("STUDY")

    assert structure.study_key == "STUDY"
    assert structure.intervals[0].forms[0].variables[0].variable_name == "V1"
