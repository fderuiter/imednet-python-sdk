Configuration
=============

The SDK and CLI read settings from environment variables. They can be set in the
shell or stored in a ``.env`` file that the CLI loads automatically via
:func:`dotenv.load_dotenv`. Load these values into a typed
:class:`~imednet.config.Config` with :func:`~imednet.config.load_config`—see
:doc:`imednet.config` for details.

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
