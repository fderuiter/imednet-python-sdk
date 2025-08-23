from __future__ import annotations

import typer

from imednet.testing.data_dictionary import app as data_dictionary_app

app = typer.Typer(help="Testing commands.")

app.add_typer(
    data_dictionary_app,
    name="data-dictionary",
    help="Commands for handling data dictionaries.",
)
