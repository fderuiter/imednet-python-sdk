.. _usage-initialization-auth:

Initialization and Authentication
=================================

To start using the iMednet Python SDK, you first need to initialize the main client class, :class:`~imednet_sdk.client.ImednetClient`.

Importing the Client
--------------------

First, import the client class into your Python script:

.. code-block:: python

   from imednet_sdk import ImednetClient

Authentication Methods
----------------------

The SDK requires your iMednet API Key and Security Key for authentication. You can provide these credentials in two primary ways:

1. **Directly during Initialization**

   You can pass the keys directly to the client constructor using the ``api_key`` and ``security_key`` arguments:

   .. code-block:: python

      client = ImednetClient(
          api_key="YOUR_API_KEY",
          security_key="YOUR_SECURITY_KEY"
      )

   Replace ``"YOUR_API_KEY"`` and ``"YOUR_SECURITY_KEY"`` with your actual credentials.

2. **Using Environment Variables**

   Alternatively, the client can automatically read the credentials from environment variables. Set the following variables in your environment:

   * ``IMEDNET_API_KEY``
   * ``IMEDNET_SECURITY_KEY``

   **Example (Bash/Zsh):**

   .. code-block:: bash

      export IMEDNET_API_KEY='your_api_key'
      export IMEDNET_SECURITY_KEY='your_security_key'

   **Example (PowerShell):**

   .. code-block:: powershell

      $env:IMEDNET_API_KEY='your_api_key'
      $env:IMEDNET_SECURITY_KEY='your_security_key'

   If these environment variables are set, you can initialize the client without passing the keys directly:

   .. code-block:: python

      # Client automatically reads credentials from environment variables
      client = ImednetClient()

   .. note::
      Credentials passed directly during initialization take precedence over environment variables.

Other Initialization Options
----------------------------

The :class:`~imednet_sdk.client.ImednetClient` constructor also accepts other optional arguments:

* ``base_url``: Override the default iMednet API base URL (``https://api.imednet.com``).
* ``timeout``: Set the default timeout for API requests (in seconds).

.. code-block:: python

   client = ImednetClient(
       base_url="https://sandbox.imednet.com", # Example for a sandbox environment
       timeout=30.0 # Set timeout to 30 seconds
       # Credentials can still be passed or read from env vars
   )

Using the Client as a Context Manager
-------------------------------------

The client is designed to be used as a context manager (using a ``with`` statement). This ensures that the underlying HTTP session is properly managed and closed.

.. code-block:: python

   from imednet_sdk import ImednetClient

   try:
       with ImednetClient() as client:
           # Make API calls using the client instance
           studies = client.studies.list_studies()
           print(f"Found {studies.metadata.total_count} studies.")
           # ... other operations ...

   except Exception as e:
       print(f"An error occurred: {e}")

   # The client session is automatically closed when exiting the 'with' block

This is the recommended way to use the client to ensure resources are handled correctly.
