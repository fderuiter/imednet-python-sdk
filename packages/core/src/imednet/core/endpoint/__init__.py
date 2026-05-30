"""
Core endpoint abstractions and protocols.
"""

from .base import AsyncListGetEndpoint, GenericEndpoint, GenericListGetEndpoint, SyncListGetEndpoint
from .edc_mixin import EdcAsyncGenericListGetEndpoint, EdcAsyncListGetEndpoint, EdcGenericListGetEndpoint, EdcSyncListGetEndpoint
from .protocols import SupportsCreate, SupportsGet, SupportsList

__all__ = [
    "EdcGenericListGetEndpoint",
    "EdcAsyncGenericListGetEndpoint",
    "EdcSyncListGetEndpoint",
    "EdcAsyncListGetEndpoint",
    "SyncListGetEndpoint",
    "AsyncListGetEndpoint",
    "GenericEndpoint",
    "GenericListGetEndpoint",
    "SupportsCreate",
    "SupportsGet",
    "SupportsList",
]
