Configuration
=============

The SDK and CLI read settings from environment variables. They can be set in the
shell or stored in a ``.env`` file that the CLI loads automatically via
:func:`dotenv.load_dotenv`.

Environment Variables
---------------------

``IMEDNET_API_KEY``
    API key used for authentication.

``IMEDNET_SECURITY_KEY``
    Security key used for authentication.

``IMEDNET_BASE_URL``
    Optional base URL for private deployments.

``IMEDNET_STUDY_KEY``
    Study identifier used by examples and some tests.

``IMEDNET_RUN_E2E``
    Set to ``1`` to enable end-to-end tests that hit a live environment.

``IMEDNET_BATCH_ID``
    Batch identifier used by job polling tests. Created automatically if unset.

``IMEDNET_FORM_KEY``
    Form key for record-creation tests. If unset, the first form is used.

``IMEDNET_ALLOW_MUTATION``
    Set to ``1`` to allow workflow tests that submit data.

Using a .env File
-----------------

Create a ``.env`` file in the project root to store the variables above::

    IMEDNET_API_KEY=your_api_key
    IMEDNET_SECURITY_KEY=your_security_key
    IMEDNET_BASE_URL=https://example.com

The CLI loads this file automatically. Other scripts can call
``dotenv.load_dotenv()`` to mimic this behaviour.

Parsing Values
--------------

When reading environment variables or other untyped values, use helpers from
:mod:`imednet.utils.validators` such as
:func:`imednet.utils.validators.parse_bool`,
:func:`imednet.utils.validators.parse_datetime`,
:func:`imednet.utils.validators.parse_int_or_default`,
:func:`imednet.utils.validators.parse_str_or_default`,
:func:`imednet.utils.validators.parse_list_or_default`, and
:func:`imednet.utils.validators.parse_dict_or_default`.

.. code-block:: python

   >>> from imednet.utils.validators import (
   ...     parse_bool,
   ...     parse_datetime,
   ...     parse_int_or_default,
   ...     parse_str_or_default,
   ...     parse_list_or_default,
   ...     parse_dict_or_default,
   ... )
   >>> parse_bool("yes")
   True
   >>> parse_datetime("2020-01-01T00:00:00Z").year
   2020
   >>> parse_int_or_default("bad", default=5)
   5
   >>> parse_str_or_default(1.23)
   '1.23'
   >>> parse_list_or_default("x")
   ['x']
   >>> parse_dict_or_default(None)
   {}
