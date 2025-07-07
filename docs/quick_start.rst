Quick Start
===========

This page walks through a minimal example of using the SDK.

Install the package from PyPI:

.. code-block:: console

   pip install imednet

Set your credentials as environment variables:

.. code-block:: bash

   export IMEDNET_API_KEY="your_api_key"
   export IMEDNET_SECURITY_KEY="your_security_key"

Enable structured logging and list studies:

.. code-block:: python

   from imednet import ImednetSDK, load_config
   from imednet.utils import configure_json_logging

   configure_json_logging()
   cfg = load_config()
   sdk = ImednetSDK(
       api_key=cfg.api_key,
       security_key=cfg.security_key,
       base_url=cfg.base_url,
   )
   studies = sdk.studies.list()
   print(studies)

The example script :mod:`examples.quick_start` provides a runnable version that
validates required environment variables.

Cached endpoints can be refreshed with ``refresh=True``. The caches are not thread safe so long running applications should recreate the SDK when needed.
