from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich import print

from imednet.validation import DataDictionaryLoader

app = typer.Typer(help="Data dictionary commands.")


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
    if zip_file:
        dd = DataDictionaryLoader.from_zip(zip_file)
        print(f"Loaded data dictionary from {zip_file.name}")
    elif all([business_logic_file, choices_file, forms_file, questions_file]):
        dd = DataDictionaryLoader.from_files(
            business_logic=business_logic_file,
            choices=choices_file,
            forms=forms_file,
            questions=questions_file,
        )
        print("Loaded data dictionary from individual files.")
    else:
        print(
            "Error: You must provide either --zip-file or all four CSV file options."
        )
        raise typer.Exit(code=1)

    print(dd)
