Query Aging Workflow
====================

The ``QueryAgingWorkflow`` provides helper methods to analyze the age of open
queries in a study. The :meth:`aging_summary` method returns a count of open
queries grouped by configurable age buckets.

Example
-------

.. code-block:: python

   from imednet.sdk import ImednetSDK
   from imednet.workflows.query_aging import QueryAgingWorkflow

   sdk = ImednetSDK(api_key="<API_KEY>", security_key="<SECURITY_KEY>")
   workflow = QueryAgingWorkflow(sdk)
   summary = workflow.aging_summary("MY_STUDY")
   print(summary)
