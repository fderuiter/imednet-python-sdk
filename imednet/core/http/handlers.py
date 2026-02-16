"""
HTTP response handling and error mapping.
"""

from __future__ import annotations

import httpx

from imednet.core.exceptions import (
    ApiError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    UnauthorizedError,
)

STATUS_TO_ERROR: dict[int, type[ApiError]] = {
    400: BadRequestError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
    429: RateLimitError,
}


def handle_response(response: httpx.Response) -> httpx.Response:
    """Return the response or raise an appropriate ``ApiError``."""
    if response.is_error:
        status = response.status_code
        try:
            body = response.json()
        except Exception:
            body = response.text
        exc_cls = STATUS_TO_ERROR.get(status)
        if exc_cls:
            raise exc_cls(body, status_code=status)
        if 500 <= status < 600:
            raise ServerError(body, status_code=status)
        raise ApiError(body, status_code=status)
    return response
