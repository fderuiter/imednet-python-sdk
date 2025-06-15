Job Polling Mechanism
=====================

:class:`~imednet.workflows.job_poller.JobPoller` waits for background jobs to
finish. It repeatedly checks the job status until a terminal state is reached or
a timeout occurs.

.. mermaid::

   graph TD
       A[start wait()] --> B[get job status]
       B --> C{terminal state?}
       C -- Yes --> D[return status]
       C -- No --> E{timeout exceeded?}
       E -- Yes --> F[raise JobTimeoutError]
       E -- No --> G[sleep interval]
       G --> B
