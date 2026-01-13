from imednet.form_designer.builder import FormBuilder
from imednet.form_designer.presets import PRESETS


def test_demo_form_preset():
    builder = FormBuilder()
    PRESETS["Demo Form"](builder)
    layout = builder.build()
    assert len(layout.pages) == 1
    # Check for expected fields
    # Section, Group, Text, Number, Radio, Datetime, Memo
    types = []
    for entity in layout.pages[0].entities:
        if entity.props.type == "table":
            for row in entity.rows:
                # Check col 2 for control
                if len(row.cols) > 1 and row.cols[1].entities:
                    types.append(row.cols[1].entities[0].props.type)
        else:
            types.append(entity.props.type)

    assert "sep" in types
    assert "text" in types
    assert "number" in types
    assert "radio" in types
    assert "datetime" in types
    assert "memo" in types

def test_cv_pathology_preset():
    builder = FormBuilder()
    PRESETS["CV Pathology"](builder)
    layout = builder.build()
    assert len(layout.pages) == 1
