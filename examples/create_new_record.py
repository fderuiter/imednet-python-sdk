# examples/create_new_record.py
"""
Example: Creating a New Record via iMednet API.

This script demonstrates how to use the `imednet-python-sdk` to create a new
record for a specific form, subject, site, and visit within an iMednet study.

**Prerequisites:**

1.  **Install SDK:** `pip install imednet-sdk python-dotenv`
2.  **Environment Variables:** Create a `.env` file in the same directory
    with your iMednet API key and base URL:
    ```
    IMEDNET_API_KEY="your_api_key_here"
    IMEDNET_SECURITY_KEY="your_security_key_here"
    IMEDNET_BASE_URL="https://your_imednet_instance.imednetapi.com"
    ```
3.  **Configuration:** Update the `TARGET_STUDY_KEY`, `TARGET_SUBJECT_KEY`,
    `TARGET_FORM_KEY`, `TARGET_SITE_NAME`, and `TARGET_INTERVAL_NAME` constants
    below with valid values from your iMednet study.
4.  **Record Data:** Modify the `NEW_RECORD_DATA` dictionary to include the
    actual variable names (keys) and corresponding values for the specific
    form you are targeting.

**Usage:**

```bash
python examples/create_new_record.py
```

The script will attempt to create the record and log the outcome, including
the batch ID of the background job initiated by iMednet.
"""

import logging
import os
from datetime import datetime

from dotenv import load_dotenv

from imednet_sdk import ImednetClient
from imednet_sdk.exceptions import ImednetSdkException
from imednet_sdk.models import RecordPostItem

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("IMEDNET_API_KEY")
BASE_URL = os.getenv("IMEDNET_BASE_URL")

# --- Configuration ---
# Specify the Study Key, Subject Key, Form Key, Site Name, and Interval Name
TARGET_STUDY_KEY = "DEMO"  # Replace with a valid Study Key
TARGET_SUBJECT_KEY = "SUBJ-001"  # Replace with a valid Subject Key
TARGET_FORM_KEY = "AE"  # Replace with the Key of the form to create a record for
TARGET_SITE_NAME = "Site 01"  # Replace with the Name of the subject's site
TARGET_INTERVAL_NAME = "Screening"  # Replace with the Name of the relevant interval/visit

# Define the data for the new record. Keys MUST be the `variableName` from the form definition.
# Values MUST match the expected data type for each variable.
NEW_RECORD_DATA = {
    # --- Form-Specific Data Items ---
    # Replace these with actual variableNames and values for your form (TARGET_FORM_KEY)
    "AETERM": "Headache",
    "AESEV": "Mild",  # Assuming AESEV expects a string based on dropdown/radio choices
    "AESTDAT": datetime.now().strftime("%Y-%m-%d"),  # Example date format, adjust if needed
    # ... add all required and optional data items for the form ...
}
# ---------------------


def main():
    """Initializes the client, prepares record data, and calls the create_records endpoint."""
    if not API_KEY or not BASE_URL:
        logging.error(
            "API Key or Base URL not configured. Set IMEDNET_API_KEY and "
            "IMEDNET_BASE_URL environment variables."
        )
        return

    if any(
        val == "PLACEHOLDER"
        for val in [
            TARGET_STUDY_KEY,
            TARGET_SUBJECT_KEY,
            TARGET_FORM_KEY,
            TARGET_SITE_NAME,
            TARGET_INTERVAL_NAME,
        ]
    ):
        logging.warning(
            "Please replace placeholder Keys/Names (e.g., DEMO, SUBJ-001) with actual values in the script."
        )
        return

    if (
        "AETERM" in NEW_RECORD_DATA and TARGET_FORM_KEY == "AE"
    ):  # Basic check if example data might still be present
        logging.info(
            "Using example data for AE form. Ensure this matches your study configuration."
        )
        # Consider adding a more robust check or removing this if statement

    try:
        # Initialize the client (using environment variables for keys)
        client = ImednetClient(base_url=BASE_URL)
        logging.info("iMednet client initialized successfully.")

        # --- Prepare Record Payload ---
        # Create an instance of the RecordPostItem model
        record_to_create = RecordPostItem(
            formKey=TARGET_FORM_KEY,
            siteName=TARGET_SITE_NAME,
            subjectKey=TARGET_SUBJECT_KEY,
            intervalName=TARGET_INTERVAL_NAME,
            data=NEW_RECORD_DATA,
        )

        # --- Create New Record(s) ---
        # The create_records method takes a list of RecordPostItem objects
        logging.info(
            f"Attempting to create a new record for form '{TARGET_FORM_KEY}' "
            f"for subject '{TARGET_SUBJECT_KEY}'..."
        )

        # Call the SDK method which corresponds to POST /records
        # This returns a JobStatusModel indicating the background job status
        job_status = client.records.create_records(
            study_key=TARGET_STUDY_KEY,
            records=[record_to_create],
            # Optionally add email_notify="your.email@example.com"
        )

        if job_status and job_status.batchId:
            logging.info(
                f"Successfully initiated record creation job. Batch ID: {job_status.batchId}"
            )
            logging.info(f"Initial job state: {job_status.state}")
            logging.info("Use the JobsClient or check the iMednet UI to monitor job completion.")
            logging.debug(f"Job status details: {job_status}")
        else:
            logging.error(
                "Record creation call completed but did not return expected job status or batch ID."
            )

    except ImednetSdkException as e:
        logging.error(f"An API error occurred during record creation initiation: {e}")
        logging.error(
            f"Status Code: {e.status_code}, API Code: {e.api_error_code}, " f"Message: {e.message}"
        )

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()
