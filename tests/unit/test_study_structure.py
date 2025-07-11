import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from imednet.models.forms import Form
from imednet.models.intervals import FormSummary, Interval
from imednet.models.variables import Variable
from imednet.workflows.study_structure import async_get_study_structure, get_study_structure


@pytest.mark.parametrize("async_mode", [False, True])
def test_get_study_structure_aggregates_related_data(async_mode: bool) -> None:
    sdk = MagicMock()
    interval = Interval(
        interval_id=1,
        interval_name="INT1",
        interval_sequence=1,
        interval_description="desc",
        interval_group_name="grp",
        forms=[FormSummary(form_id=1, form_key="F1", form_name="Form1")],
    )
    form = Form(form_id=1, form_key="F1", form_name="Form1")
    variable = Variable(variable_id=1, variable_name="V1", label="Var 1", form_id=1)

    if async_mode:
        sdk.intervals.async_list = AsyncMock(return_value=[interval])
        sdk.forms.async_list = AsyncMock(return_value=[form])
        sdk.variables.async_list = AsyncMock(return_value=[variable])
        structure = asyncio.run(async_get_study_structure(sdk, "STUDY"))
        sdk.intervals.async_list.assert_awaited_once_with("STUDY")
        sdk.forms.async_list.assert_awaited_once_with("STUDY")
        sdk.variables.async_list.assert_awaited_once_with("STUDY")
    else:
        sdk.intervals.list.return_value = [interval]
        sdk.forms.list.return_value = [form]
        sdk.variables.list.return_value = [variable]
        structure = get_study_structure(sdk, "STUDY")
        sdk.intervals.list.assert_called_once_with("STUDY")
        sdk.forms.list.assert_called_once_with("STUDY")
        sdk.variables.list.assert_called_once_with("STUDY")

    assert structure.study_key == "STUDY"
    assert structure.intervals[0].forms[0].variables[0].variable_name == "V1"
