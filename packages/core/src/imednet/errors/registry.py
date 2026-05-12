"""Registry for HTTP status code to error class mappings."""

from __future__ import annotations

import types
from typing import Mapping, Type

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
STATUS_TO_ERROR: Mapping[int, Type[ApiError]] = types.MappingProxyType(
    {
        400: BadRequestError,
        401: UnauthorizedError,
        403: ForbiddenError,
        404: NotFoundError,
        409: ConflictError,
        429: RateLimitError,
    }
)


def get_error_class(status_code: int) -> Type[ApiError]:
    """
    Get error class for status code.

    Defaults to generic ApiError for unmapped client/server errors.
    """
    error_cls = STATUS_TO_ERROR.get(status_code)
    if error_cls:
        return error_cls
    if 500 <= status_code < 600:
        return ServerError
    return ApiError
