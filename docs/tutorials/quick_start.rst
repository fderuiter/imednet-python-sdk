Quick Start
===========

This page walks through a minimal example of using the SDK.

Installation
------------

.. code-block:: bash

   # PyPI release
   pip install imednet

   # Install all tabular export dependencies
   pip install "imednet[export]"

   # Or install destination-specific extras
   pip install "imednet[duckdb]"
   pip install "imednet[mongodb]"
   pip install "imednet[neo4j]"
   pip install "imednet[snowflake]"

   # Workflow plugin package
   pip install imednet-workflows

   # Airflow provider package (core hook/operator/sensor support)
   pip install "apache-airflow>=2.3.0,<4.0.0" apache-airflow-providers-imednet


Basic Usage
-----------

Set your credentials by copying the environment template or exporting them directly:

.. code-block:: bash

   cp .env.example .env
   export IMEDNET_API_KEY="your_api_key"
   export IMEDNET_SECURITY_KEY="your_security_key"


Synchronous Example
-------------------

.. literalinclude:: /../examples/quick_start.py
   :language: python
   :start-after: """
   :end-before: """


Asynchronous Example
--------------------

.. literalinclude:: /../examples/async_quick_start.py
   :language: python
   :start-after: """
   :end-before: """


Custom retry logic can be provided via a ``RetryPolicy``:

.. testcode::

   from imednet.core.retry import RetryPolicy, RetryState
   from imednet.errors import ServerError

   class ServerRetry(RetryPolicy):
       def should_retry(self, state: RetryState) -> bool:
           return isinstance(state.exception, ServerError)

   sdk = ImednetSDK(retry_policy=ServerRetry())

See :doc:`/how-to/retry_policy` for more guidance on error handling and exponential
backoff.
