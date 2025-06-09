import os

from imednet.sdk import ImednetSDK
from imednet.workflows.credential_validation import CredentialValidationWorkflow

"""Example for validating credentials using the CredentialValidationWorkflow.

This script initializes the SDK with API credentials and uses the
``CredentialValidationWorkflow`` to verify that the study key provided exists
in the list of accessible studies. It also demonstrates validating credentials
from the ``IMEDNET_STUDY_KEY`` environment variable using the
``validate_environment`` method.

Prerequisites:
    - Set ``IMEDNET_API_KEY`` and ``IMEDNET_SECURITY_KEY`` environment variables.
    - Optionally set ``IMEDNET_BASE_URL`` and ``IMEDNET_STUDY_KEY``.
"""

api_key = os.getenv("IMEDNET_API_KEY")
security_key = os.getenv("IMEDNET_SECURITY_KEY")
base_url = os.getenv("IMEDNET_BASE_URL")  # Optional
study_key = os.getenv("IMEDNET_STUDY_KEY", "your_study_key_here")

if not api_key or not security_key:
    raise RuntimeError(
        "IMEDNET_API_KEY and IMEDNET_SECURITY_KEY environment variables must be set."
    )

try:
    sdk = ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)
    workflow = CredentialValidationWorkflow(sdk)

    if workflow.validate(study_key):
        print(f"Credentials are valid for study '{study_key}'.")
    else:
        print(f"Study '{study_key}' not found. Check the study key or credentials.")

    # Validate using the IMEDNET_STUDY_KEY environment variable (raises ValueError if unset)
    if workflow.validate_environment():
        print("Environment credentials validated successfully.")
except Exception as e:
    print(f"Error validating credentials: {e}")
