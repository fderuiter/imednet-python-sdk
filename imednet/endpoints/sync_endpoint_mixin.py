"""Shared sync helpers for endpoint wrappers."""

from __future__ import annotations

from typing import Any

from imednet.core.paginator import Paginator


class SyncEndpointMixin:
    """Mixin providing sync ``list`` and ``get`` helpers."""

    def list(self: Any, *args: Any, **kwargs: Any) -> Any:
        """Delegate to ``_list_impl`` using :class:`Paginator`."""
        if args:
            if len(args) == 1 and "study_key" not in kwargs:
                kwargs["study_key"] = args[0]
            else:
                raise TypeError("Invalid positional arguments")
        return self._list_impl(self._client, Paginator, **kwargs)

    def get(self: Any, identifier: Any, *args: Any, **kwargs: Any) -> Any:
        """Delegate to ``_get_impl`` using :class:`Paginator`."""
        if args:
            raise TypeError("Invalid positional arguments")
        return self._get_impl(self._client, Paginator, identifier, **kwargs)
