from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich import print

from imednet.validation import DataDictionary, DataDictionaryLoader

app = typer.Typer(help="Data dictionary commands.")


def _load_dd_from_options(
    zip_file: Optional[Path],
    business_logic_file: Optional[Path],
    choices_file: Optional[Path],
    forms_file: Optional[Path],
    questions_file: Optional[Path],
) -> DataDictionary:
    """Load a data dictionary from either a ZIP file or individual CSV files.

    Args:
        zip_file: The path to the ZIP file.
        business_logic_file: The path to the BUSINESS_LOGIC.csv file.
        choices_file: The path to the CHOICES.csv file.
        forms_file: The path to the FORMS.csv file.
        questions_file: The path to the QUESTIONS.csv file.

    Returns:
        The loaded DataDictionary object.

    Raises:
        typer.Exit: If the required file options are not provided.
    """
    if zip_file:
        return DataDictionaryLoader.from_zip(zip_file)
    if all([business_logic_file, choices_file, forms_file, questions_file]):
        assert business_logic_file is not None
        assert choices_file is not None
        assert forms_file is not None
        assert questions_file is not None
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
    """Load and print a data dictionary from a ZIP file or individual CSV files.

    Args:
        zip_file: The path to the ZIP file.
        business_logic_file: The path to the BUSINESS_LOGIC.csv file.
        choices_file: The path to the CHOICES.csv file.
        forms_file: The path to the FORMS.csv file.
        questions_file: The path to the QUESTIONS.csv file.
    """
    dd = _load_dd_from_options(
        zip_file, business_logic_file, choices_file, forms_file, questions_file
    )
    print("Loaded data dictionary.")
    print(dd)
