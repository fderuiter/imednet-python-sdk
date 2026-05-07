"""
Core endpoint abstractions and protocols.
"""

from .base import GenericEndpoint, GenericListGetEndpoint
from .protocols import SupportsCreate, SupportsGet, SupportsList

__all__ = [
    "GenericEndpoint",
    "GenericListGetEndpoint",
    "SupportsCreate",
    "SupportsGet",
    "SupportsList",
]
