from __future__ import annotations

from typing import List, Optional

from .json_base import JsonModel


class ApiErrorDetail(JsonModel):
    """
    Represents the structure of an error response from the API.
    """

    type: Optional[str] = None
    title: Optional[str] = None
    status: Optional[int] = None
    detail: Optional[str] = None
    instance: Optional[str] = None
    errors: Optional[List[str]] = None
