"""Registry for HTTP status code to error class mappings."""

from __future__ import annotations

import types
from collections.abc import Mapping
from typing import Any

from .api import (
    ApiError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    UnauthorizedError,
)
from .validation import BadRequestError

# Use MappingProxyType to ensure immutability, avoiding global mutable state
STATUS_TO_ERROR: Mapping[int, type[ApiError]] = types.MappingProxyType(
    {
        400: BadRequestError,
        401: UnauthorizedError,
        403: ForbiddenError,
        404: NotFoundError,
        409: ConflictError,
        429: RateLimitError,
    }
)


def get_error_class(status_code: int, response_body: Any = None) -> type[ApiError]:
    """Get error class for status code.

    Defaults to generic ApiError for unmapped client/server errors.
    """
    if isinstance(response_body, dict):
        status = response_body.get("status")
        # Identify specific subclasses based on metadata
        if status_code == 400 and status == "validation_error":
            from .validation import ValidationError

            return ValidationError
        if status_code == 401 and status == "authentication_failed":
            from .api import AuthenticationError

            return AuthenticationError

    error_cls = STATUS_TO_ERROR.get(status_code)
    if error_cls:
        return error_cls
    if 500 <= status_code < 600:
        return ServerError
    return ApiError
