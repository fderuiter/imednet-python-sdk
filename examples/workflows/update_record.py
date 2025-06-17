import os

from imednet import ImednetSDK
from imednet.workflows import JobPoller, RecordUpdateWorkflow

"""Examples for all ``RecordUpdateWorkflow`` POST scenarios.

The script demonstrates how to:

1. Register a new subject.
2. Update a scheduled record.
3. Create an unscheduled record for an existing subject.

Each step submits the record and then waits for the asynchronous job to finish
using :class:`JobPoller`. Credentials default to the ``IMEDNET_*`` environment
variables if set. Replace any remaining placeholders with real identifiers
before running the script.
"""

api_key = os.getenv("IMEDNET_API_KEY", "XXXXXXXXXX")
security_key = os.getenv("IMEDNET_SECURITY_KEY", "XXXXXXXXXX")
base_url = os.getenv("IMEDNET_BASE_URL")
study_key = os.getenv("IMEDNET_STUDY_KEY", "XXXXXXXXXX")
form_key = "XXXXXXXXXX"  # Registration or visit form key
site_name = "XXXXXXXXXX"  # Site for new subject registration
interval_name = "XXXXXXXXXX"  # Interval for updating a scheduled record
subject_key = "XXXXXXXXXX"  # Existing subject key

sdk = ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)
workflow = RecordUpdateWorkflow(sdk)

record_data = {"VARIABLE_NAME": "value"}

# 1. Register a new subject
try:
    job = workflow.register_subject(
        study_key=study_key,
        form_identifier=form_key,
        site_identifier=site_name,
        data=record_data,
        wait_for_completion=False,
    )

    if not job.batch_id:
        raise RuntimeError("Registration succeeded but no batch ID returned")

    status = JobPoller(sdk, study_key, job.batch_id).wait()
    print(f"Registration job {status.batch_id} finished with state: {status.state}")
except Exception as e:
    print(f"Error registering subject: {e}")

# 2. Update a scheduled record
try:
    job = workflow.update_scheduled_record(
        study_key=study_key,
        form_identifier=form_key,
        subject_identifier=subject_key,
        interval_identifier=interval_name,
        data=record_data,
        wait_for_completion=False,
    )

    if not job.batch_id:
        raise RuntimeError("Update succeeded but no batch ID returned")

    status = JobPoller(sdk, study_key, job.batch_id).wait()
    print(f"Update job {status.batch_id} finished with state: {status.state}")
except Exception as e:
    print(f"Error updating scheduled record: {e}")

# 3. Create an unscheduled record
try:
    job = workflow.create_new_record(
        study_key=study_key,
        form_identifier=form_key,
        subject_identifier=subject_key,
        data=record_data,
        wait_for_completion=False,
    )

    if not job.batch_id:
        raise RuntimeError("Creation succeeded but no batch ID returned")

    status = JobPoller(sdk, study_key, job.batch_id).wait()
    print(f"Creation job {status.batch_id} finished with state: {status.state}")
except Exception as e:
    print(f"Error creating record: {e}")
