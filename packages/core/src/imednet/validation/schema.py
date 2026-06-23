"""TODO: Add docstring."""

from __future__ import annotations

import warnings

from .cache import AsyncSchemaValidator, BaseSchemaCache, SchemaValidator, validate_record_data

warnings.warn(
    "imednet.validation.schema is deprecated; use imednet.validation.cache "
    "(deprecated in 0.7.0, to be removed in 0.9.0)",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "BaseSchemaCache",
    "SchemaValidator",
    "AsyncSchemaValidator",
    "validate_record_data",
]
