Register Subjects Workflow
==========================

The ``RegisterSubjectsWorkflow`` validates that site names exist before submitting registration records.
The API assigns the subject identifier upon creation; do not include a ``subjectKey`` in the request.

Example
-------

.. testcode::

    from imednet import ImednetSDK
    from imednet.models.records import RegisterSubjectRequest, RecordData
    from imednet_workflows.register_subjects import RegisterSubjectsWorkflow
    from typing import Any, cast

    sdk = ImednetSDK(api_key="API_KEY", security_key="SECURITY_KEY")
    workflow = RegisterSubjectsWorkflow(cast(Any, sdk))
    subjects = [RegisterSubjectRequest(formKey="REG", siteName="SITE", data=RecordData({}))]
    job = workflow.register_subjects(study_key="STUDY", subjects=subjects)
    print(job)
