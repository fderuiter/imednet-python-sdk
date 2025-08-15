from __future__ import annotations

import os
import sys

from imednet import ImednetSDK
from imednet.integrations import export_to_long_sql

"""Export records to a normalized long-format SQL table.

Set ``IMEDNET_API_KEY`` and ``IMEDNET_SECURITY_KEY`` before running this script.
Optionally set ``IMEDNET_BASE_URL`` for non-default instances.

Usage:
    python examples/export_long_sql.py STUDY_KEY TABLE_NAME OUTPUT_DB

The ``OUTPUT_DB`` path is used to build the SQLite connection string.
"""


def main() -> None:
    """Export a study's records in long format to SQLite."""

    if len(sys.argv) != 4:
        print(
            "Usage: python examples/export_long_sql.py STUDY_KEY TABLE_NAME OUTPUT_DB",
            file=sys.stderr,
        )
        sys.exit(1)

    study_key, table_name, output_db = sys.argv[1:]

    missing = [var for var in ("IMEDNET_API_KEY", "IMEDNET_SECURITY_KEY") if not os.getenv(var)]
    if missing:
        vars_ = ", ".join(missing)
        print(f"Missing required environment variable(s): {vars_}", file=sys.stderr)
        sys.exit(1)

    sdk = ImednetSDK()
    conn_str = f"sqlite:///{output_db}"
    export_to_long_sql(sdk, study_key, table_name, conn_str)
    print(f"Exported {study_key} to {output_db} using table '{table_name}'.")


if __name__ == "__main__":
    main()
