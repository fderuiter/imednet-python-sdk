"""
Service Provider Interface (SPI) for Imednet Extensions.

This module provides a stable public interface for advanced platform developers,
plugins, and providers, decoupling them from internal core implementation details.
"""

from imednet.integrations import export, sink_base

from . import cli, constants, endpoints, errors, facade, models, security, utils, validation

__all__ = [
    "cli",
    "constants",
    "endpoints",
    "errors",
    "export",
    "facade",
    "models",
    "security",
    "sink_base",
    "utils",
    "validation",
]
