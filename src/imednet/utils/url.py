from __future__ import annotations

import re
from typing import Any, Optional, Set
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import httpx

__all__ = ["sanitize_base_url", "redact_url_query", "build_safe_path"]


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


def build_safe_path(base_path: str, *segments: Any) -> str:
    """Construct a safe URL path using :class:`httpx.URL` normalization.

    Avoids double-encoding bugs by relying on httpx's native RFC-3986
    compliance instead of manually quoting every path segment.  Characters
    that are valid inside a URL path (e.g. ``@``, ``:``) are preserved as-is,
    while structural delimiters (``?``, ``#``) and path-traversal sequences
    are handled automatically by the URL parser.

    Args:
        base_path: The leading path prefix (e.g. ``"/api/v1/edc/studies"``).
        *segments: Additional path segments to append.  Each segment is
            converted to a string and stripped of surrounding slashes before
            joining.

    Returns:
        The normalised path string (always starts with ``/``).
    """
    string_segments = [str(seg).strip("/") for seg in segments if seg is not None]

    if not string_segments:
        return base_path

    joined_segments = "/".join(string_segments)
    raw_path = f"{base_path.rstrip('/')}/{joined_segments}"

    # Pass through httpx.URL to normalise the path and handle safe encoding.
    # A dummy base is used solely to leverage the URL parser's path handling.
    normalized_url = httpx.URL("http://dummy").join(raw_path)
    return normalized_url.path
