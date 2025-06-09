import os

from imednet.sdk import ImednetSDK
from imednet.workflows.subject_data import SubjectDataWorkflow

"""Example for retrieving comprehensive subject information using
:class:`SubjectDataWorkflow`.

The script requires the subject key via ``IMEDNET_SUBJECT_KEY`` and prints the
aggregated data including visits, records, and queries.
"""

api_key = os.getenv("IMEDNET_API_KEY")
security_key = os.getenv("IMEDNET_SECURITY_KEY")
base_url = os.getenv("IMEDNET_BASE_URL")
study_key = os.getenv("IMEDNET_STUDY_KEY", "your_study_key_here")
subject_key = os.getenv("IMEDNET_SUBJECT_KEY", "your_subject_key_here")

if not api_key or not security_key:
    raise RuntimeError(
        "IMEDNET_API_KEY and IMEDNET_SECURITY_KEY environment variables must be set."
    )

sdk = ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)
workflow = SubjectDataWorkflow(sdk)

try:
    data = workflow.get_all_subject_data(study_key, subject_key)
    print(data.model_dump())
except Exception as e:
    print(f"Error retrieving subject data: {e}")
