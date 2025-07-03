from __future__ import annotations

import warnings

from .cache import BaseSchemaCache, SchemaValidator, validate_record_data

warnings.warn(
    "imednet.validation.schema is deprecated; use imednet.validation.cache",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "BaseSchemaCache",
    "SchemaValidator",
    "validate_record_data",
]
