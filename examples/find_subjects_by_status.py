# examples/find_subjects_by_status.py
"""
Example: Finding Subjects by Status via iMednet API.

This script demonstrates how to use the `imednet-python-sdk` to retrieve a list
of subjects within a specific study, filtered by their current status (e.g.,
"Enrolled", "Screening", "Completed").

**Prerequisites:**

1.  **Install SDK:** `pip install imednet-sdk python-dotenv`
2.  **Environment Variables:** Create a `.env` file in the same directory
    with your iMednet API key, security key, and base URL:
    ```
    IMEDNET_API_KEY="your_api_key_here"
    IMEDNET_SECURITY_KEY="your_security_key_here"
    IMEDNET_BASE_URL="https://your_imednet_instance.imednetapi.com"
    ```
3.  **Configuration:** Update the `TARGET_STUDY_KEY` and `TARGET_SUBJECT_STATUS`
    constants below with valid values from your iMednet study.

**Usage:**

```bash
python examples/find_subjects_by_status.py
```

The script will query the API for subjects matching the specified status in the
target study and print their details.
"""

import logging
import os

from dotenv import load_dotenv

from imednet_sdk import ImednetClient
from imednet_sdk.exceptions import ImednetSdkException

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("IMEDNET_API_KEY")
SECURITY_KEY = os.getenv("IMEDNET_SECURITY_KEY")
BASE_URL = os.getenv("IMEDNET_BASE_URL")

# --- Configuration ---
# Specify the Study Key and the desired Subject Status to filter by
TARGET_STUDY_KEY = "DEMO"  # Replace with a valid Study Key from your iMednet instance
TARGET_SUBJECT_STATUS = (
    "Enrolled"  # Replace with a valid status (e.g., "Enrolled", "Screen Failed", "Completed")
)
# ---------------------


def main():
    """Initializes the client and fetches subjects filtered by status."""
    if not API_KEY or not SECURITY_KEY or not BASE_URL:
        logging.error(
            "API Key, Security Key, or Base URL not configured. Set IMEDNET_API_KEY, "
            "IMEDNET_SECURITY_KEY, and IMEDNET_BASE_URL environment variables."
        )
        return

    if TARGET_STUDY_KEY == "DEMO":
        logging.warning(
            "Using default 'DEMO' study key. Please replace with your actual Study Key if needed."
        )

    try:
        # Initialize the client (using environment variables for keys)
        client = ImednetClient(base_url=BASE_URL)
        logging.info("iMednet client initialized successfully.")

        # --- Find Subjects by Status ---
        print(
            f"Fetching subjects with status '{TARGET_SUBJECT_STATUS}' "
            f"in study '{TARGET_STUDY_KEY}'..."
        )

        # Use the list_subjects method with the filter parameter
        # The filter syntax uses == for equality and property names from the API model
        subject_filter = f'subjectStatus=="{TARGET_SUBJECT_STATUS}"'

        # The list_subjects method returns an ApiResponse object
        response = client.subjects.list_subjects(
            study_key=TARGET_STUDY_KEY,
            filter=subject_filter,
            size=500,  # Optional: Increase page size if expecting many subjects
        )

        # Check if the response contains data
        if not response or not response.data:
            logging.warning(
                f"No subjects found with status '{TARGET_SUBJECT_STATUS}' "
                f"in study '{TARGET_STUDY_KEY}'. "
                f"Response: {response}"
            )
            return

        subjects = response.data
        logging.info(f"Found {len(subjects)} subject(s) with status '{TARGET_SUBJECT_STATUS}'.")

        # Print details of the found subjects
        for subject in subjects:
            logging.info(
                f"  - Subject Key: {subject.subjectKey}, Site: {subject.siteName}, "
                f"Status: {subject.subjectStatus}"
            )

    except ImednetSdkException as e:
        logging.error(f"An API error occurred: {e}")
        logging.error(
            f"Status Code: {e.status_code}, API Code: {e.api_error_code}, " f"Message: {e.message}"
        )


if __name__ == "__main__":
    main()
