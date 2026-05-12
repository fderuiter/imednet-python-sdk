"""
Core endpoint abstractions and protocols.
"""

from .base import GenericEndpoint, GenericListGetEndpoint
from .edc_mixin import EdcGenericListGetEndpoint
from .protocols import SupportsCreate, SupportsGet, SupportsList

__all__ = [
    "EdcGenericListGetEndpoint",
    "GenericEndpoint",
    "GenericListGetEndpoint",
    "SupportsCreate",
    "SupportsGet",
    "SupportsList",
]
