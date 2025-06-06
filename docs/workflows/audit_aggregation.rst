AuditAggregationWorkflow
========================

The :class:`~imednet.workflows.audit_aggregation.AuditAggregationWorkflow`
provides helper methods to summarize audit trail information from the
``recordRevisions`` endpoint.

Summary by user
---------------

``summary_by_user`` aggregates record revision counts for each user within a
specified date range. The method fetches the revisions via the SDK and groups
them client side.

Example usage::

   from imednet.sdk import ImednetSDK
   from imednet.workflows.audit_aggregation import AuditAggregationWorkflow

   sdk = ImednetSDK(api_key="<API>", security_key="<SEC>")
   wf = AuditAggregationWorkflow(sdk)
   counts = wf.summary_by_user(
       study_key="MY_STUDY",
       start_date="2024-01-01",
       end_date="2024-01-31",
       site_id=1,
   )
   print(counts)

This returns a dictionary mapping each username to the number of revisions they
performed during the period.
