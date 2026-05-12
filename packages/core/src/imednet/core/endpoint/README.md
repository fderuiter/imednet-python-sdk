# Core Endpoint Abstractions

This directory contains the base classes, operations, and protocols for SDK endpoints.

*   `base.py`: Defines generic endpoint classes and composes list/get behavior using operation classes.
*   `operations/`: Provides reusable operation classes for list/get/create execution.
*   `protocols.py`: Defines structural typing protocols for endpoint and operation interfaces.

These components are designed to be extended by concrete endpoint implementations in `imednet/endpoints/`.
