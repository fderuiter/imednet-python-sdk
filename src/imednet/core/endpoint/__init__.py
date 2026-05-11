"""
Core endpoint abstractions and protocols.
"""

from .base import GenericEndpoint, GenericListGetEndpoint
from .cached_mixin import CachedEndpointMixin
from .protocols import SupportsCreate, SupportsGet, SupportsList

__all__ = [
    "GenericEndpoint",
    "CachedEndpointMixin",
    "GenericListGetEndpoint",
    "SupportsCreate",
    "SupportsGet",
    "SupportsList",
]
