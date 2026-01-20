from __future__ import annotations

import re
from urllib.parse import urlparse, urlunparse

__all__ = ["sanitize_base_url", "redact_url_query"]


def sanitize_base_url(url: str) -> str:
    """Return base URL without trailing slashes or ``/api`` suffix."""
    url = url.rstrip("/")
    return re.sub(r"/api\Z", "", url)


def redact_url_query(url: str) -> str:
    """Return URL with query parameters replaced by 'REDACTED'."""
    parsed = urlparse(url)
    if parsed.query:
        return urlunparse(parsed._replace(query="REDACTED"))
    return url
