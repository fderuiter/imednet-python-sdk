"""Placeholder for common type aliases."""

from typing import Any, Dict, List, Union

# Purpose:
# This module defines common type aliases used throughout the SDK codebase
# for better readability and type hinting consistency.

# Implementation:
# 1. Define aliases for frequently used complex types:
#    - `JsonDict = Dict[str, Any]` (or similar for JSON objects)
#    - `JsonList = List[Any]` (or similar for JSON arrays)
#    - `JsonType = Union[JsonDict, JsonList, str, int, float, bool, None]`
#    - `DataFrame` (if pandas is a dependency): `from pandas import DataFrame`
#    - Potentially aliases for specific ID types if they are strings/ints but used distinctly.

# Integration:
# - Imported and used in type hints across `core`, `endpoints`, `models`, `workflows`, and `utils`.
# - Improves code clarity and maintainability.

JsonDict = Dict[str, Any]
JsonList = List[Any]
JsonType = Union[JsonDict, JsonList, str, int, float, bool, None]

# Example if pandas is used:
# try:
#     from pandas import DataFrame
# except ImportError:
#     DataFrame = Any # type: ignore
