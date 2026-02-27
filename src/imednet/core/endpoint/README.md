# Core Endpoint Abstractions

This directory contains the base classes and mixins for SDK endpoints.

*   `base.py`: Defines `BaseEndpoint`, handling context injection and basic path building.
*   `mixins.py`: Provides reusable logic for listing, filtering, and parsing resources (e.g., `ListGetEndpointMixin`).

These components are designed to be extended by concrete endpoint implementations in `imednet/endpoints/`.
