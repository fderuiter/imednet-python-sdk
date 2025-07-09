Retry Policy
============

``RetryPolicy`` decouples retry decisions from the underlying tenacity logic.
The default implementation only retries for network errors raised by ``httpx``.
You can implement your own strategy by inspecting :class:`imednet.core.retry.RetryState`.

Example
-------

.. code-block:: python

   from imednet.core.client import Client
   from imednet.core.retry import RetryPolicy, RetryState
   from imednet.core.exceptions import ServerError

   class ServerRetry(RetryPolicy):
       def should_retry(self, state: RetryState) -> bool:
           return isinstance(state.exception, ServerError)

   client = Client("A", "B", retry_policy=ServerRetry())
