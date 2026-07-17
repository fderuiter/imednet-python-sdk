"""Compatibility facades for exposing internal endpoint methods safely."""

from typing import Any


def is_async_client(sdk: Any) -> bool:
    """Check if the SDK is using an async client."""
    return getattr(sdk, "_async_client", None) is not None


def execute_list_sync(endpoint: Any, study_key: str | None = None, **filters: Any) -> Any:
    """Stable facade to execute synchronous list operations on endpoints."""
    list_sync = getattr(endpoint, "_list_sync", None)
    require_sync_client = getattr(endpoint, "_require_sync_client", None)
    paginator_cls = getattr(endpoint, "PAGINATOR_CLS", None)

    if not callable(list_sync) or not callable(require_sync_client) or paginator_cls is None:
        raise NotImplementedError("Endpoint does not support sync list via compatibility facade.")

    return list_sync(
        require_sync_client(),
        paginator_cls,
        study_key=study_key,
        **filters,
    )


def execute_list_async(endpoint: Any, study_key: str | None = None, **filters: Any) -> Any:
    """Stable facade to execute asynchronous list operations on endpoints."""
    list_async = getattr(endpoint, "_list_async", None)
    require_async_client = getattr(endpoint, "_require_async_client", None)
    paginator_cls = getattr(endpoint, "PAGINATOR_CLS", None)

    if not callable(list_async) or not callable(require_async_client) or paginator_cls is None:
        raise NotImplementedError("Endpoint does not support async list via compatibility facade.")

    return list_async(
        require_async_client(),
        paginator_cls,
        study_key=study_key,
        **filters,
    )
