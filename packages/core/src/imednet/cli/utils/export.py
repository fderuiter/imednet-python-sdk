"""CLI utilities for exporting data to files."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, Protocol, Sequence

import typer
from rich import print

from imednet.utils import sanitize_csv_formula


class Model(Protocol):
    """Protocol for objects that can be dumped to a dictionary."""

    def model_dump(self, *, by_alias: bool = False) -> Dict[str, Any]:
        """Dump the model to a dictionary."""
        ...


def export_list_to_file(
    items: Sequence[Model],
    filename_prefix: str,
    output_format: str,
) -> None:
    """Export a list of Pydantic models to a file.

    Handles CSV and JSON formats. Sanitize CSV data to prevent injection.
    """
    fmt = output_format.lower()
    if fmt not in {"csv", "json"}:
        print(f"[bold red]Error:[/bold red] Invalid output format: '{fmt}'. Supported: csv, json.")
        raise typer.Exit(code=1)

    path = Path(f"{filename_prefix}.{fmt}")

    # Export full data
    # We use by_alias=True to match the API response structure
    data = [item.model_dump(by_alias=True) for item in items]

    if fmt == "csv":
        if data:
            # Sanitize data to prevent CSV injection
            for row in data:
                for k, v in row.items():
                    row[k] = sanitize_csv_formula(v)

            keys = data[0].keys()
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
        else:
            # Create empty file
            path.touch()
    else:
        # JSON export
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    print(f"Saved {len(items)} {filename_prefix} to {path}")
