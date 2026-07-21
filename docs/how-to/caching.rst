Caching Behavior
================

This page explains how the SDK handles data caching.

Endpoint Caching
----------------

The SDK no longer maintains any stateful in-memory cache on endpoint instances.
Every call to ``list()`` performs a fresh API request,
ensuring that concurrent requests from different application contexts cannot
contaminate each other's data.

If your application needs to reduce redundant API calls, implement caching at
the application layer using a library such as `cachetools`_, a request-level
cache middleware (e.g. ``httpx-cache``), or your framework's own cache
primitives (e.g. Django's cache framework or FastAPI dependency injection).

.. _cachetools: https://cachetools.readthedocs.io/

Schema Cache
------------

:class:`~imednet.validation.cache.SchemaCache` stores variable metadata by form
key to validate record payloads locally. It can be populated explicitly via
``SchemaCache.refresh()`` using the :class:`~imednet.endpoints.forms.FormsEndpoint`
and :class:`~imednet.endpoints.variables.VariablesEndpoint` or lazily through
:class:`~imednet.validation.cache.SchemaValidator` when validation is performed.

The cache maps each form key to a dictionary of variables and also tracks form
IDs. ``SchemaValidator`` looks up the form key for a record and fetches metadata
on demand if it has not been cached yet.

For offline tests, ``imednet.testing.fake_data`` includes helpers to generate
forms, variables and records. These objects can be used with
``SchemaCache.refresh`` to validate payloads without hitting the API.
