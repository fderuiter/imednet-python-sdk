"""Deterministic example values for variable types.

Used in tests and smoke scripts to exercise typed fields.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

# Maps variable type synonyms to example values.
_TYPED_VALUES: Dict[str, Any] = {
    "string": "example",
    "text": "example",
    "memo": "example memo",
    "date": "2024-01-01",
    "number": 1,
    "int": 1,
    "integer": 1,
    "float": 1.0,
    "decimal": 1.0,
    "radio": "1",
    "dropdown": "1",
    "checkbox": True,
}

# Maps variable type synonyms to canonical categories.
_CANONICAL_TYPES: Dict[str, str] = {
    "string": "string",
    "text": "string",
    "memo": "memo",
    "date": "date",
    "number": "number",
    "int": "number",
    "integer": "number",
    "float": "number",
    "decimal": "number",
    "radio": "radio",
    "dropdown": "dropdown",
    "checkbox": "checkbox",
}


def canonical_type(var_type: str) -> Optional[str]:
    """Get the canonical type for a given variable type string.

    This is used to group synonyms like "int" and "integer" under a single
    canonical type like "number".

    Args:
        var_type: The variable type string.

    Returns:
        The canonical type string, or `None` if the type is not supported.
    """
    return _CANONICAL_TYPES.get(var_type.lower())


def value_for(var_type: str) -> Optional[Any]:
    """Get a deterministic example value for a given variable type.

    This is useful for creating test data with predictable values.

    Args:
        var_type: The variable type string.

    Returns:
        An example value for the type, or `None` if the type is not supported.
    """
    return _TYPED_VALUES.get(var_type.lower())
