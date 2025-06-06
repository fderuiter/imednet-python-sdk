Visit Tracking Workflow
=======================

The ``VisitTrackingWorkflow`` aggregates visit completion for all subjects in a study.
It uses :class:`~imednet.workflows.visit_completion.VisitCompletionWorkflow` to
compute each subject's progress and returns the results keyed by subject key.

Example usage::

   from imednet.sdk import ImednetSDK
   from imednet.workflows.visit_tracking import VisitTrackingWorkflow

   sdk = ImednetSDK(api_key="<API_KEY>", security_key="<SECURITY_KEY>")
   workflow = VisitTrackingWorkflow(sdk)
   progress = workflow.summary_by_subject("MY_STUDY")
   print(progress)
