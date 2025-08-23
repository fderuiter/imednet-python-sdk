from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich import print

from imednet.sdk import ImednetSDK
from imednet.testing.record_generator import RecordGenerator
from imednet.validation import DataDictionary, DataDictionaryLoader

app = typer.Typer(help="Data dictionary commands.")


def _load_dd_from_options(
    zip_file: Optional[Path],
    business_logic_file: Optional[Path],
    choices_file: Optional[Path],
    forms_file: Optional[Path],
    questions_file: Optional[Path],
) -> DataDictionary:
    if zip_file:
        return DataDictionaryLoader.from_zip(zip_file)
    if all([business_logic_file, choices_file, forms_file, questions_file]):
        return DataDictionaryLoader.from_files(
            business_logic=business_logic_file,
            choices=choices_file,
            forms=forms_file,
            questions=questions_file,
        )
    print("Error: You must provide either --zip-file or all four CSV file options.")
    raise typer.Exit(code=1)


@app.command("load")
def load_data_dictionary(
    zip_file: Optional[Path] = typer.Option(
        None,
        "--zip-file",
        "-z",
        help="Path to a ZIP file containing the data dictionary.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    business_logic_file: Optional[Path] = typer.Option(
        None,
        "--business-logic-file",
        help="Path to BUSINESS_LOGIC.csv.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    choices_file: Optional[Path] = typer.Option(
        None,
        "--choices-file",
        help="Path to CHOICES.csv.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    forms_file: Optional[Path] = typer.Option(
        None,
        "--forms-file",
        help="Path to FORMS.csv.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    questions_file: Optional[Path] = typer.Option(
        None,
        "--questions-file",
        help="Path to QUESTIONS.csv.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
) -> None:
    """Load and print a data dictionary from a ZIP file or individual CSV files."""
    dd = _load_dd_from_options(
        zip_file, business_logic_file, choices_file, forms_file, questions_file
    )
    print("Loaded data dictionary.")
    print(dd)


@app.command("generate-records")
def generate_records(
    ctx: typer.Context,
    form_key: str = typer.Option(
        ..., "--form", help="The key of the form to generate records for."
    ),
    study_key: str = typer.Option(..., "--study", help="The key of the study to submit to."),
    subject_key: str = typer.Option(..., "--subject", help="The key of the subject to submit for."),
    zip_file: Optional[Path] = typer.Option(
        None,
        "--zip-file",
        "-z",
        help="Path to a ZIP file containing the data dictionary.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    business_logic_file: Optional[Path] = typer.Option(
        None,
        "--business-logic-file",
        help="Path to BUSINESS_LOGIC.csv.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    choices_file: Optional[Path] = typer.Option(
        None,
        "--choices-file",
        help="Path to CHOICES.csv.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    forms_file: Optional[Path] = typer.Option(
        None,
        "--forms-file",
        help="Path to FORMS.csv.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    questions_file: Optional[Path] = typer.Option(
        None,
        "--questions-file",
        help="Path to QUESTIONS.csv.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    wait: bool = typer.Option(False, "--wait", help="Wait for the job to complete."),
) -> None:
    """Generate and submit a new record for a form."""
    dd = _load_dd_from_options(
        zip_file, business_logic_file, choices_file, forms_file, questions_file
    )
    print("Loaded data dictionary.")

    sdk = ImednetSDK()
    generator = RecordGenerator(sdk, dd)

    print(f"Generating and submitting record for form '{form_key}'...")
    job = generator.generate_and_submit_form(
        form_key=form_key,
        study_key=study_key,
        subject_identifier=subject_key,
        wait_for_completion=wait,
    )

    print("Record submission initiated.")
    print(job)
