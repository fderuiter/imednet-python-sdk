Quick Start
===========

This page walks through a minimal example of using the SDK.

.. include:: ../README.md
   :parser: myst_parser.sphinx_
   :start-after: ## Installation
   :end-before: ### 🖥 Streamlit Dashboard

.. include:: ../README.md
   :parser: myst_parser.sphinx_
   :start-after: ## Quick Start
   :end-before: See [docs/async_quick_start.rst](docs/async_quick_start.rst) for more details.

Custom retry logic can be provided via a ``RetryPolicy``:


.. testcode::

   from imednet.core.retry import RetryPolicy, RetryState
   from imednet.errors import ServerError

   class ServerRetry(RetryPolicy):
       def should_retry(self, state: RetryState) -> bool:
           return isinstance(state.exception, ServerError)

   sdk = ImednetSDK(retry_policy=ServerRetry())

See :doc:`retry_policy` for more guidance on error handling and exponential
backoff.
