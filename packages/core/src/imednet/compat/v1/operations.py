"""
Compatibility facades for aliasing divergent operational patterns.
"""

from typing import Any, Optional

def get_resource_sync(endpoint: Any, study_key: Optional[str], item_id: Any) -> Any:
    """Stable facade for retrieving a single resource, aliasing path vs filter patterns."""
    return endpoint.get(study_key, item_id)

def get_resource_async(endpoint: Any, study_key: Optional[str], item_id: Any) -> Any:
    """Stable facade for retrieving a single resource, aliasing path vs filter patterns."""
    return endpoint.async_get(study_key, item_id)
