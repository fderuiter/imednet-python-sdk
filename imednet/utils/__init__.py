"""
Re-exports utility functions for easier access.
"""

from .dates import format_iso_datetime, parse_iso_datetime
from .filters import build_filter_string
from .json_logging import configure_json_logging
from .typing import DataFrame, JsonDict


def __getattr__(name: str):
    if name in {"records_to_dataframe", "export_records_csv"}:
        from .pandas import export_records_csv, records_to_dataframe

        globals().update(
            {
                "records_to_dataframe": records_to_dataframe,
                "export_records_csv": export_records_csv,
            }
        )
        return globals()[name]
    if name in {"SchemaCache", "validate_record_data", "SchemaValidator"}:
        from .schema import SchemaCache, SchemaValidator, validate_record_data

        globals().update(
            {
                "SchemaCache": SchemaCache,
                "validate_record_data": validate_record_data,
                "SchemaValidator": SchemaValidator,
            }
        )
        return globals()[name]
    if name in {
        "parse_bool",
        "parse_datetime",
        "parse_int_or_default",
        "parse_str_or_default",
        "parse_list_or_default",
        "parse_dict_or_default",
    }:
        from .validators import (
            parse_bool,
            parse_datetime,
            parse_dict_or_default,
            parse_int_or_default,
            parse_list_or_default,
            parse_str_or_default,
        )

        globals().update(
            {
                "parse_bool": parse_bool,
                "parse_datetime": parse_datetime,
                "parse_int_or_default": parse_int_or_default,
                "parse_str_or_default": parse_str_or_default,
                "parse_list_or_default": parse_list_or_default,
                "parse_dict_or_default": parse_dict_or_default,
            }
        )
        return globals()[name]

    raise AttributeError(name)


__all__ = [
    "parse_iso_datetime",
    "format_iso_datetime",
    "build_filter_string",
    "configure_json_logging",
    "records_to_dataframe",
    "export_records_csv",
    "JsonDict",
    "DataFrame",
    "SchemaCache",
    "validate_record_data",
    "SchemaValidator",
    "parse_bool",
    "parse_datetime",
    "parse_int_or_default",
    "parse_str_or_default",
    "parse_list_or_default",
    "parse_dict_or_default",
]
