from __future__ import annotations

from typing import Callable, Type

from .base import BaseEndpoint

_ENDPOINT_REGISTRY: dict[str, Type[BaseEndpoint]] = {}


def register_endpoint(name: str) -> Callable:
    """
    A decorator to register endpoint classes.
    """

    def decorator(cls: Type[BaseEndpoint]) -> Type[BaseEndpoint]:
        _ENDPOINT_REGISTRY[name] = cls
        return cls

    return decorator


def get_endpoint_registry() -> dict[str, Type[BaseEndpoint]]:
    """
    Return the endpoint registry.
    """
    return _ENDPOINT_REGISTRY
