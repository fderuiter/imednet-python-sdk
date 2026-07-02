"""Endpoints package for the iMedNet SDK.

This package contains dynamically generated API endpoint implementations 
for accessing iMedNet resources based on the unified manifest.
"""
from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY

__all__ = ["ENDPOINT_REGISTRY", "ASYNC_ENDPOINT_REGISTRY"]
