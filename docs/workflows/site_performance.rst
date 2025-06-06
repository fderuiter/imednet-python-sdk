Site Performance Workflow
=========================

The :class:`~imednet.workflows.site_performance.SitePerformanceWorkflow` helps
summarize enrollment and query metrics for each site in a study.

Example usage::

   from imednet.sdk import ImednetSDK
   from imednet.workflows.site_performance import SitePerformanceWorkflow

   sdk = ImednetSDK(api_key="<API_KEY>", security_key="<SECURITY_KEY>")
   workflow = SitePerformanceWorkflow(sdk)
   metrics = workflow.get_site_metrics("MY_STUDY")
   print(metrics)

``metrics`` is a :class:`pandas.DataFrame` with columns:

- ``site_id`` – numeric site identifier
- ``site_name`` – name of the site
- ``site_enrollment_status`` – current enrollment status
- ``subject_count`` – number of subjects registered at the site
- ``open_query_count`` – count of open queries linked to subjects at the site
