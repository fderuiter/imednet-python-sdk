from __future__ import annotations

import re

__all__ = ["sanitize_base_url"]


def sanitize_base_url(url: str) -> str:
    """Sanitize a base URL by removing trailing slashes and any `/api` suffix.

    Args:
        url: The URL to sanitize.

    Returns:
        The sanitized URL.
    """
    url = url.strip(" /")
    return re.sub(r"/api\Z", "", url, flags=re.IGNORECASE)
