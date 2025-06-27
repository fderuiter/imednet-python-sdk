import json
import os

from imednet import ImednetSDK
from imednet.workflows.register_subjects import RegisterSubjectsWorkflow

"""
Example script demonstrating how to register multiple subjects in an iMednet study.
This script initializes the ImednetSDK and the RegisterSubjectsWorkflow.
It reads subject data from a JSON file (`sample_subjects.json`) located
in the ``register_subjects_input`` subdirectory relative to the script's location.
A copy of ``sample_subjects.json`` is included in this repository under
``examples/register_subjects_input`` for reference.
The script then uses the workflow's ``register_subjects`` method to register all
subjects defined in the JSON file for the specified study.
The script requires API credentials (api_key, security_key) and the study_key
to be set. The base_url can optionally be set for custom iMednet instances.
It prints the result of the registration process or an error message if
the registration fails.
Attributes:
    api_key (str): The API key for iMednet authentication.
    security_key (str): The security key for iMednet authentication.
    base_url (str | None): The base URL of the iMednet instance. Defaults to None,
        which uses the standard iMednet production URL.
    study_key (str): The unique identifier for the target study.
    input_path (str): The file path to the JSON file containing the subject data.
"""

api_key = "XXXXXXXXXX"
security_key = "XXXXXXXXXX"
base_url = None  # Or set to your custom base URL if needed
study_key = "XXXXXXXXXX"

# Path to the sample input file included with this repository
input_path = os.path.join(
    os.path.dirname(__file__), "register_subjects_input", "sample_subjects.json"
)

try:
    sdk = ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)
    workflow = RegisterSubjectsWorkflow(sdk)

    with open(input_path, "r", encoding="utf-8") as f:
        subjects = json.load(f)

    # Register all subjects at once
    result = workflow.register_subjects(study_key=study_key, subjects=subjects)
    print(f"Registered {len(subjects)} subjects. Result: {result}")
except Exception as e:
    print(f"Error registering subjects: {e}")
