from imednet.form_designer.builder import FormBuilder
from imednet.form_designer.models import Layout


def test_builder_initialization():
    builder = FormBuilder()
    assert len(builder.pages) == 1
    assert len(builder.pages[0].entities) == 0

def test_add_page():
    builder = FormBuilder()
    builder.add_page()
    assert len(builder.pages) == 2

def test_add_section_header():
    builder = FormBuilder()
    builder.add_section_header("My Section")
    assert len(builder.current_page.entities) == 1
    entity = builder.current_page.entities[0]
    assert entity.props.type == "sep"
    assert entity.props.label == "My Section"
    assert entity.id.startswith("lfdiv_")

def test_add_group_header():
    builder = FormBuilder()
    builder.add_group_header("My Group")
    # Should create a table with one row
    assert len(builder.current_page.entities) == 1
    table = builder.current_page.entities[0]
    assert table.props.type == "table"
    assert len(table.rows) == 1
    row = table.rows[0]
    # Group header: Col 1 has label, Col 2 is empty
    assert len(row.cols) == 2
    assert row.cols[0].entities[0].props.type == "label"
    assert row.cols[0].entities[0].props.label == "My Group"
    assert len(row.cols[1].entities) == 0

def test_add_field_text():
    builder = FormBuilder()
    builder.add_field(
        type="text",
        label="My Field",
        question_name="VAR1",
        required=True,
        max_length=50
    )
    table = builder.current_page.entities[0]
    row = table.rows[0]

    # Label
    label_entity = row.cols[0].entities[0]
    assert label_entity.props.type == "label"
    assert label_entity.props.label == "My Field"

    # Control
    control_entity = row.cols[1].entities[0]
    assert control_entity.props.type == "text"
    assert control_entity.props.question_name == "VAR1"
    assert control_entity.props.bl_req == "hard"
    assert control_entity.props.length == 50

    # ID Linking
    assert label_entity.props.new_fld_id == control_entity.props.new_fld_id
    assert label_entity.props.new_fld_id is not None

def test_add_field_radio():
    builder = FormBuilder()
    choices = [("Yes", "1"), ("No", "0")]
    builder.add_field(
        type="radio",
        label="Gender",
        question_name="SEX",
        choices=choices
    )
    control = builder.current_page.entities[0].rows[0].cols[1].entities[0]
    assert control.props.type == "radio"
    assert len(control.props.choices) == 2
    assert control.props.choices[0].text == "Yes"
    assert control.props.choices[0].code == "1"
    assert control.props.radio == 1  # Horizontal default

def test_add_field_datetime():
    builder = FormBuilder()
    builder.add_field("datetime", "Date", "DT")
    control = builder.current_page.entities[0].rows[0].cols[1].entities[0]
    assert control.props.type == "datetime"
    assert control.props.date_ctrl == 1
    assert control.props.time_ctrl == 0

def test_build():
    builder = FormBuilder()
    builder.add_section_header("S1")
    layout = builder.build()
    assert isinstance(layout, Layout)
    assert len(layout.pages) == 1
