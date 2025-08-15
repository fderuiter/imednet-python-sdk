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
    """Return the canonical type for ``var_type`` or ``None`` if unsupported."""

    return _CANONICAL_TYPES.get(var_type.lower())


def value_for(var_type: str) -> Optional[Any]:
    """Return a deterministic example value for ``var_type`` if supported."""

    return _TYPED_VALUES.get(var_type.lower())
