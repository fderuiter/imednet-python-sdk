"""Helper utilities for endpoint implementations."""

from __future__ import annotations

from typing import Any, Dict, Optional, Type

from imednet.core.async_paginator import AsyncPaginator
from imednet.core.paginator import Paginator
from imednet.utils.filters import build_filter_string


def build_paginator(
    endpoint: Any,
    paginator_cls: Type[Paginator] | Type[AsyncPaginator],
    resource: str,
    study_key: Optional[str],
    page_size: Optional[int],
    filters: Optional[Dict[str, Any]] = None,
    *,
    extra_params: Optional[Dict[str, Any]] = None,
    require_study: bool = True,
) -> Paginator | AsyncPaginator:
    """Return a paginator for the given endpoint resource."""
    filter_params: Dict[str, Any] = endpoint._auto_filter(filters or {})
    if study_key:
        filter_params["studyKey"] = study_key

    study = filter_params.pop("studyKey", None)
    if require_study and not study:
        raise ValueError("Study key must be provided or set in the context")

    params: Dict[str, Any] = {}
    filter_arg = filter_params.pop("filter", None)
    if filter_arg:
        params["filter"] = (
            filter_arg if isinstance(filter_arg, str) else build_filter_string(filter_arg)
        )
    elif filter_params:
        params["filter"] = build_filter_string(filter_params)

    if extra_params:
        params.update(extra_params)

    base_args = []
    if study:
        base_args.append(study)
    if resource:
        base_args.append(resource)
    path = endpoint._build_path(*base_args)
    return paginator_cls(
        endpoint._client,
        path,
        params=params,
        page_size=page_size or endpoint._default_page_size,
    )
