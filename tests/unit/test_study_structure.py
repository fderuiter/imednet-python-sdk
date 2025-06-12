from unittest.mock import MagicMock

from imednet.models.forms import Form
from imednet.models.intervals import FormSummary, Interval
from imednet.models.variables import Variable
from imednet.workflows.study_structure import get_study_structure


def test_get_study_structure_aggregates_related_data(monkeypatch) -> None:
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

    sdk.intervals.list.return_value = [interval]
    sdk.forms.list.return_value = [form]
    sdk.variables.list.return_value = [variable]

    # patch model_dump to exclude forms key to avoid duplicate parameters
    orig_dump = Interval.model_dump
    monkeypatch.setattr(
        Interval,
        "model_dump",
        lambda self: {k: v for k, v in orig_dump(self).items() if k != "forms"},
    )

    structure = get_study_structure(sdk, "STUDY")

    sdk.intervals.list.assert_called_once_with("STUDY")
    sdk.forms.list.assert_called_once_with("STUDY")
    sdk.variables.list.assert_called_once_with("STUDY")

    assert structure.study_key == "STUDY"
    assert structure.intervals[0].forms[0].variables[0].variable_name == "V1"
