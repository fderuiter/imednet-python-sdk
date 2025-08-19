Async Quick Start
=================

This page shows a minimal asynchronous example using ``AsyncImednetSDK``.

Install the package from PyPI:

.. code-block:: console

   pip install imednet

Set your credentials as environment variables:

.. code-block:: bash

   export IMEDNET_API_KEY="your_api_key"
   export IMEDNET_SECURITY_KEY="your_security_key"

List studies asynchronously and poll a job:

.. code-block:: python

   import asyncio
   from imednet import AsyncImednetSDK, load_config
   from imednet.utils import configure_json_logging

   async def main() -> None:
       configure_json_logging()
       cfg = load_config()
       async with AsyncImednetSDK(
           api_key=cfg.api_key,
           security_key=cfg.security_key,
           base_url=cfg.base_url,
       ) as sdk:
           studies = await sdk.studies.async_list()
           print(studies)
           status = await sdk.async_poll_job("STUDY", "BATCH", interval=2, timeout=60)
           print(status)


   asyncio.run(main())

For synchronous usage, see :doc:`quick_start`.

The example script :doc:`examples/async_quick_start` provides a runnable version that
validates required environment variables and optionally polls a job when
``IMEDNET_JOB_STUDY_KEY`` and ``IMEDNET_BATCH_ID`` are set.
