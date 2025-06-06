Subject Enrollment Dashboard
===========================

The :class:`~imednet.workflows.subject_enrollment_dashboard.SubjectEnrollmentDashboard` class
combines site and subject information to track recruitment progress and dropout rates.

Example usage::

    from imednet.sdk import ImednetSDK
    from imednet.workflows.subject_enrollment_dashboard import SubjectEnrollmentDashboard

    sdk = ImednetSDK(api_key="API_KEY", security_key="SECURITY_KEY")
    dashboard = SubjectEnrollmentDashboard(sdk)
    df = dashboard.build("STUDY_KEY")
    print(df.head())

