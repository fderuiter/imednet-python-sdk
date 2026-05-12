from __future__ import annotations

import re
from typing import Optional, Set
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

__all__ = ["sanitize_base_url", "redact_url_query"]


def sanitize_base_url(url: str) -> str:
    """Return base URL without trailing slashes or ``/api`` suffix."""
    url = url.rstrip("/")
    return re.sub(r"/api\Z", "", url)


def redact_url_query(url: str, sensitive_params: Optional[Set[str]] = None) -> str:
    """Return URL with sensitive query parameters redacted."""
    if sensitive_params is None:
        sensitive_params = {"api_key", "security_key", "token", "secret", "password"}

    parsed = urlparse(url)
    query_params = parse_qsl(parsed.query, keep_blank_values=True)

    new_query_params = []
    for key, value in query_params:
        if key in sensitive_params:
            new_query_params.append((key, "***"))
        else:
            new_query_params.append((key, value))

    new_query = urlencode(new_query_params, safe="*")
    return urlunparse(parsed._replace(query=new_query))
