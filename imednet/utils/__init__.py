"""
Re-exports utility functions for easier access.
"""

from importlib import import_module

from .dates import format_iso_datetime, parse_iso_datetime
from .filters import build_filter_string
from .json_logging import configure_json_logging
from .typing import DataFrame, JsonDict

_LAZY_ATTRS: dict[str, tuple[str, str]] = {
    "records_to_dataframe": ("imednet.utils.pandas", "records_to_dataframe"),
    "export_records_csv": ("imednet.utils.pandas", "export_records_csv"),
    "parse_bool": ("imednet.utils.validators", "parse_bool"),
    "parse_datetime": ("imednet.utils.validators", "parse_datetime"),
    "parse_int_or_default": ("imednet.utils.validators", "parse_int_or_default"),
    "parse_str_or_default": ("imednet.utils.validators", "parse_str_or_default"),
    "parse_list_or_default": ("imednet.utils.validators", "parse_list_or_default"),
    "parse_dict_or_default": ("imednet.utils.validators", "parse_dict_or_default"),
    "sanitize_base_url": ("imednet.utils.url", "sanitize_base_url"),
}


def __getattr__(name: str):  # noqa: D401
    try:
        module_path, obj_name = _LAZY_ATTRS[name]
    except KeyError:
        raise AttributeError(name) from None
    mod = import_module(module_path)
    obj = getattr(mod, obj_name)
    globals()[name] = obj
    return obj


__all__ = [
    "parse_iso_datetime",
    "format_iso_datetime",
    "build_filter_string",
    "configure_json_logging",
    "records_to_dataframe",
    "export_records_csv",
    "JsonDict",
    "DataFrame",
    "parse_bool",
    "parse_datetime",
    "parse_int_or_default",
    "parse_str_or_default",
    "parse_list_or_default",
    "parse_dict_or_default",
    "sanitize_base_url",
]
