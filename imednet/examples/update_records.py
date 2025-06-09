import json
import os

from imednet.sdk import ImednetSDK
from imednet.workflows.record_update import RecordUpdateWorkflow

"""Example for submitting record batches with :class:`RecordUpdateWorkflow`.

This script reads a JSON file containing record data and submits it to the
configured study. By default it waits for the job to complete and prints the
final job state.

The expected JSON structure is a list of record dictionaries compatible with the
``records.create`` endpoint. Provide the path to the file in the
``RECORD_UPDATE_FILE`` environment variable.
"""

api_key = os.getenv("IMEDNET_API_KEY")
security_key = os.getenv("IMEDNET_SECURITY_KEY")
base_url = os.getenv("IMEDNET_BASE_URL")
study_key = os.getenv("IMEDNET_STUDY_KEY", "your_study_key_here")
file_path = os.getenv("RECORD_UPDATE_FILE", "record_update_input/sample_records.json")

if not api_key or not security_key:
    raise RuntimeError(
        "IMEDNET_API_KEY and IMEDNET_SECURITY_KEY environment variables must be set."
    )

sdk = ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)
workflow = RecordUpdateWorkflow(sdk)

try:
    with open(file_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    job = workflow.submit_record_batch(
        study_key=study_key,
        records_data=records,
        wait_for_completion=True,
        timeout=300,
    )
    print(f"Batch {job.batch_id} finished with state: {job.state}")
except Exception as e:
    print(f"Error submitting records: {e}")
