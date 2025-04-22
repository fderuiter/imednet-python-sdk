# examples/get_all_records_for_subject.py
"""
Example: Retrieving All Records for a Subject via iMednet API.

This script demonstrates how to use the `imednet-python-sdk` to retrieve all
records associated with a specific subject within a study. It handles potential
pagination by repeatedly calling the `list_records` endpoint until all pages
have been fetched.

**Prerequisites:**

1.  **Install SDK:** `pip install imednet-sdk python-dotenv`
2.  **Environment Variables:** Create a `.env` file in the same directory
    with your iMednet API key, security key, and base URL:
    ```
    IMEDNET_API_KEY="your_api_key_here"
    IMEDNET_SECURITY_KEY="your_security_key_here"
    IMEDNET_BASE_URL="https://your_imednet_instance.imednetapi.com"
    ```
3.  **Configuration:** Update the `TARGET_STUDY_KEY` and `TARGET_SUBJECT_KEY`
    constants below with valid values from your iMednet study.

**Usage:**

```bash
python examples/get_all_records_for_subject.py
```

The script will query the API for all records matching the specified subject in
the target study, handling pagination, and print a summary of the retrieved records.
"""

import logging
import os
from typing import List

from dotenv import load_dotenv

from imednet_sdk import ImednetClient
from imednet_sdk.api.records import RecordModel
from imednet_sdk.exceptions import ImednetSdkException

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("IMEDNET_API_KEY")
SECURITY_KEY = os.getenv("IMEDNET_SECURITY_KEY")
BASE_URL = os.getenv("IMEDNET_BASE_URL")

# --- Configuration ---
# Specify the Study Key and Subject Key for which to retrieve records
TARGET_STUDY_KEY = "DEMO"  # Replace with a valid Study Key
TARGET_SUBJECT_KEY = "SUBJ-001"  # Replace with a valid Subject Key
PAGE_SIZE = 100  # Number of records to fetch per API call (max 500)
# ---------------------


def main():
    """Initializes the client and fetches all records for a subject, handling pagination."""
    if not API_KEY or not SECURITY_KEY or not BASE_URL:
        logging.error(
            "API Key, Security Key, or Base URL not configured. Set IMEDNET_API_KEY, "
            "IMEDNET_SECURITY_KEY, and IMEDNET_BASE_URL environment variables."
        )
        return

    if TARGET_STUDY_KEY == "DEMO" or TARGET_SUBJECT_KEY == "SUBJ-001":
        logging.warning(
            "Using default 'DEMO' study key or 'SUBJ-001' subject key. "
            "Please replace with your actual values if needed."
        )

    all_records: List[RecordModel] = []
    current_page = 0
    total_pages = 1  # Assume at least one page initially

    try:
        # Initialize the client
        client = ImednetClient(base_url=BASE_URL)
        logging.info("iMednet client initialized successfully.")

        # --- Get All Records for Subject (with Manual Pagination) ---
        logging.info(
            f"Fetching all records for subject '{TARGET_SUBJECT_KEY}' "
            f"in study '{TARGET_STUDY_KEY}'..."
        )

        # Construct the filter string
        record_filter = f'subjectKey=="{TARGET_SUBJECT_KEY}"'

        while current_page < total_pages:
            logging.info(f"Fetching page {current_page + 1} of {total_pages}...")
            try:
                response = client.records.list_records(
                    study_key=TARGET_STUDY_KEY,
                    filter=record_filter,
                    page=current_page,
                    size=PAGE_SIZE,
                    sort="recordId,asc",  # Optional: Sort for consistent ordering
                )

                if response and response.data:
                    all_records.extend(response.data)
                    logging.debug(f"  Fetched {len(response.data)} records on this page.")

                    # Update total_pages based on the first response's pagination info
                    if response.pagination:
                        total_pages = response.pagination.totalPages
                        # Basic check for safety
                        if total_pages == 0 and len(all_records) > 0:
                            logging.warning(
                                "API reported 0 total pages but records were found. "
                                "Stopping pagination."
                            )
                            break
                        elif total_pages == 0:
                            logging.info("API reported 0 total pages. No records found.")
                            break  # Exit loop if no pages reported
                    else:
                        # If pagination info is missing, assume only one page
                        logging.warning(
                            "Pagination info missing from API response. Assuming only one page."
                        )
                        break

                elif current_page == 0:
                    # No data found on the first page
                    logging.info(
                        f"No records found for subject '{TARGET_SUBJECT_KEY}' in study "
                        f"'{TARGET_STUDY_KEY}'."
                    )
                    break  # Exit loop
                else:
                    # No data on subsequent pages, should not happen if totalPages is correct
                    logging.warning(
                        f"No more data found on page {current_page + 1}, but expected "
                        f"{total_pages} total pages. Stopping pagination."
                    )
                    break

                current_page += 1

            except ImednetSdkException as e:
                logging.error(f"An API error occurred while fetching page {current_page + 1}: {e}")
                logging.error(
                    f"  Status Code: {e.status_code}, API Code: {e.api_error_code}, "
                    f"Details: {e.response_body}"
                )
                break  # Stop pagination on error
            except Exception as e:
                logging.error(f"An unexpected error occurred during pagination: {e}", exc_info=True)
                break  # Stop pagination on unexpected error

        # --- Summarize Results ---
        if all_records:
            logging.info(f"Successfully retrieved {len(all_records)} records in total.")
            # Example: Summarize by form key
            form_counts = {}
            for record in all_records:
                form_counts[record.formKey] = form_counts.get(record.formKey, 0) + 1
            form_keys_summary = ", ".join(
                [f"{key} ({count})" for key, count in form_counts.items()]
            )
            logging.info(f" Found {len(all_records)} record(s). Form Keys: {form_keys_summary}")
        elif current_page > 0:  # Check if we attempted pagination but found nothing after page 1
            logging.info(
                f"No records found for subject '{TARGET_SUBJECT_KEY}' "
                f"in study '{TARGET_STUDY_KEY}'."
            )
        # If no records were found on page 1, the message was already logged inside the loop

    except ImednetSdkException as e:
        logging.error(f"An SDK/API error occurred: {e}")
        logging.error(
            f"  Status Code: {e.status_code}, API Code: {e.api_error_code}, "
            f"Details: {e.response_body}"
        )
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()
