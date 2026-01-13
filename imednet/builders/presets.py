from typing import Callable, Dict

from imednet.builders.form_builder import FormBuilder
from imednet.models.form_designer import Layout

FormPreset = Callable[[FormBuilder], None]


def build_demo_form(builder: FormBuilder) -> None:
    """A demo form with various field types."""
    builder.add_section_header("Demographics")

    builder.add_field(
        type="text",
        label="Subject Initials",
        question_name="INIT",
        required=True,
        max_length=3
    )

    builder.add_field(
        type="number",
        label="Age",
        question_name="AGE",
        max_length=3
    )

    builder.add_field(
        type="radio",
        label="Gender",
        question_name="SEX",
        choices=[("Male", "1"), ("Female", "2")]
    )

    builder.add_section_header("Medical History")

    builder.add_group_header("General Information")

    builder.add_field(
        type="datetime",
        label="Date of Diagnosis",
        question_name="DXDATE"
    )

    builder.add_field(
        type="memo",
        label="Notes",
        question_name="NOTES"
    )

def build_cv_pathology(builder: FormBuilder) -> None:
    """A CV Pathology sample form."""
    builder.add_section_header("Cardiovascular Pathology")

    builder.add_field(
        type="text",
        label="Pathology ID",
        question_name="PATHID",
        required=True
    )

    builder.add_group_header("Specimen Details")

    builder.add_field(
        type="dropdown",
        label="Tissue Type",
        question_name="TISSUE",
        choices=[("Muscle", "1"), ("Nerve", "2"), ("Other", "99")]
    )

    builder.add_field(
        type="upload",
        label="Upload Report",
        question_name="RPTFILE"
    )


PRESETS: Dict[str, FormPreset] = {
    "Demo Form": build_demo_form,
    "CV Pathology": build_cv_pathology,
}
