Caching Behavior
================

This page explains how the SDK caches data to reduce unnecessary API calls.

Endpoint Caches
---------------

The endpoints for studies, forms, variables and intervals maintain simple in-memory
caches implemented by ``PagedEndpointMixin``. When `list()` or `async_list()` is called without any filters, the
results are stored on the endpoint instance. Subsequent calls return the cached
list instead of performing another request. Passing ``refresh=True`` bypasses the
cache and stores the fresh response.

The caches live on the endpoint instances as dictionaries keyed by study. They
are not shared across SDK instances and are discarded when the SDK is garbage
collected.

``get()`` methods use ``list(refresh=True)`` to ensure the most recent data is
returned. If your application needs to clear cached data manually you may call
``list(refresh=True)`` or create a new SDK instance.

Schema Cache
------------

:class:`~imednet.validation.schema.SchemaCache` stores variable metadata by form
key to validate record payloads locally. It can be populated explicitly via
``SchemaCache.refresh()`` using the :class:`~imednet.endpoints.forms.FormsEndpoint`
and :class:`~imednet.endpoints.variables.VariablesEndpoint` or lazily through
:class:`~imednet.validation.schema.SchemaValidator` when validation is performed.

The cache maps each form key to a dictionary of variables and also tracks form
IDs. ``SchemaValidator`` looks up the form key for a record and fetches metadata
on demand if it has not been cached yet.

For offline tests, ``imednet.testing.fake_data`` includes helpers to generate
forms, variables and records. These objects can be used with
``SchemaCache.refresh`` to validate payloads without hitting the API.

Limitations
-----------

The caching layer is purely in memory and is not thread-safe. It is intended to
minimize repeated requests in short-lived scripts or during interactive sessions.
Long running applications should periodically refresh or recreate the SDK to
avoid using stale data.
