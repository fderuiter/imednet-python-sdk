import os

from imednet.sdk import ImednetSDK
from imednet.workflows.job_monitoring import JobMonitoringWorkflow

"""Example demonstrating :class:`JobMonitoringWorkflow`.

Provide a study key and batch ID to poll job status until completion. The current
state is printed at each poll interval.

Required environment variables:
    - ``IMEDNET_API_KEY`` and ``IMEDNET_SECURITY_KEY``
    - ``IMEDNET_STUDY_KEY`` identifying the study
    - ``IMEDNET_BATCH_ID`` identifying the job batch
Optional variable ``IMEDNET_BASE_URL`` may be set for non-default environments.
"""

api_key = os.getenv("IMEDNET_API_KEY")
security_key = os.getenv("IMEDNET_SECURITY_KEY")
base_url = os.getenv("IMEDNET_BASE_URL")
study_key = os.getenv("IMEDNET_STUDY_KEY", "your_study_key_here")
batch_id = os.getenv("IMEDNET_BATCH_ID", "your_batch_id_here")

if not api_key or not security_key:
    raise RuntimeError(
        "IMEDNET_API_KEY and IMEDNET_SECURITY_KEY environment variables must be set."
    )

sdk = ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)
workflow = JobMonitoringWorkflow(sdk)


def notify(job):
    print(f"Job {job.batch_id} state: {job.state}")


try:
    final_job = workflow.wait_for_job(
        study_key=study_key,
        batch_id=batch_id,
        timeout=300,
        poll_interval=10,
        notify=notify,
    )
    print(f"Job completed with state: {final_job.state}")
except Exception as e:
    print(f"Error monitoring job: {e}")
