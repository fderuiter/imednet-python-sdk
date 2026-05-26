Quick Start
===========

This page walks through a minimal example of using the SDK.

Install the package from PyPI:

.. code-block:: console

   pip install imednet

Optional plugin packages:

.. code-block:: console

   pip install imednet-workflows
   pip install "apache-airflow>=2.3.0,<4.0.0" apache-airflow-providers-imednet
   pip install "apache-airflow>=2.3.0,<4.0.0" "apache-airflow-providers-imednet[amazon]"  # for ImednetToS3Operator

Set your credentials by copying the environment template or exporting them directly (see :doc:`configuration` for details):

.. code-block:: bash

   # Option 1: Use a .env file (recommended)
   cp .env.example .env

   # Option 2: Export directly to your shell
   export IMEDNET_API_KEY="your_api_key"
   export IMEDNET_SECURITY_KEY="your_security_key"
   # Optional: Custom base URL for the API endpoint
   # export IMEDNET_BASE_URL="https://edc.prod.imednetapi.com"

Enable structured logging and list studies:

.. code-block:: python

   from dotenv import load_dotenv
   from imednet import ImednetSDK, load_config
   from imednet.utils import configure_json_logging

   configure_json_logging()
   # Note: Ensure you've run `cp .env.example .env` or exported keys to your shell.
   load_dotenv()
   cfg = load_config()
   with ImednetSDK(
       api_key=cfg.api_key,
       security_key=cfg.security_key,
       base_url=cfg.base_url,
   ) as sdk:
       studies = sdk.studies.list()
       for study in studies:
           print(f"{study.study_name} ({study.study_key})")

The example script :doc:`examples/quick_start` provides a runnable version that
validates required environment variables.


For asynchronous usage, see :doc:`async_quick_start`.

Cached endpoints can be refreshed with ``refresh=True``. The caches are not thread safe so long running applications should recreate the SDK when needed.

Custom retry logic can be provided via a ``RetryPolicy``:

.. code-block:: python

   from imednet.core.retry import RetryPolicy, RetryState
   from imednet.errors import ServerError

   class ServerRetry(RetryPolicy):
       def should_retry(self, state: RetryState) -> bool:
           return isinstance(state.exception, ServerError)

   sdk = ImednetSDK(retry_policy=ServerRetry())

See :doc:`retry_policy` for more guidance on error handling and exponential
backoff.
