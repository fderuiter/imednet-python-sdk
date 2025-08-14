Register Subjects Workflow
==========================

The ``RegisterSubjectsWorkflow`` validates that site names and subject identifiers exist before submitting registration records.

Example
-------

.. code-block:: python

    from imednet import ImednetSDK
    from imednet.models.records import RegisterSubjectRequest
    from imednet.workflows.register_subjects import RegisterSubjectsWorkflow

    sdk = ImednetSDK(api_key="API_KEY", security_key="SECURITY_KEY")
    workflow = RegisterSubjectsWorkflow(sdk)
    subjects = [RegisterSubjectRequest(form_key="REG", site_name="SITE", subject_key="SUBJ", data={})]
    job = workflow.register_subjects(study_key="STUDY", subjects=subjects)
    print(job)
