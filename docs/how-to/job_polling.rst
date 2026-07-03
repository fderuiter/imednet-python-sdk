Job Polling Mechanism
=====================

:class:`~imednet_workflows.job_poller.JobPoller` waits for background jobs to
finish. It repeatedly checks the job status until a terminal state is reached or
a timeout occurs.

.. mermaid:: /diagrams/job_polling_2.mmd

Using the SDK
-------------

``ImednetSDK`` provides a convenience method ``poll_job`` that blocks until the
job finishes. ``AsyncImednetSDK`` exposes ``async_poll_job`` for the same
behavior in asynchronous code.

.. testcode::

   from imednet import ImednetSDK, AsyncImednetSDK

   # synchronous
   sdk = ImednetSDK()
   status = sdk.poll_job("STUDY", "BATCH", interval=2, timeout=60)

   # asynchronous
   async def wait_async():
       async with AsyncImednetSDK() as sdk:
           status = await sdk.async_poll_job("STUDY", "BATCH", interval=2, timeout=60)
