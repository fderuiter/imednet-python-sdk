"""Basic Usage Example for iMednet Python SDK.

This script provides a simple demonstration of how to initialize the
`ImednetClient` and make basic API calls to list studies and sites.

**Prerequisites:**

1.  **Install SDK:** `pip install imednet-sdk python-dotenv`
2.  **Environment Variables:** Create a `.env` file in the same directory
    with your iMednet API key, security key, and base URL:
    ```
    IMEDNET_API_KEY="your_api_key_here"
    IMEDNET_SECURITY_KEY="your_security_key_here"
    IMEDNET_BASE_URL="https://your_imednet_instance.imednetapi.com"
    ```
3.  **Replace Placeholders:** Ensure the `.env` file contains your actual
    credentials and base URL.

**Usage:**

```bash
python examples/usage_example.py
```

The script will attempt to connect to the API, list the first few studies,
and list the sites for the first study found.
"""
import os
import logging
from dotenv import load_dotenv
from imednet_sdk import ImednetClient
from imednet_sdk.exceptions import ImednetSdkException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

API_KEY = os.getenv("IMEDNET_API_KEY")
SECURITY_KEY = os.getenv("IMEDNET_SECURITY_KEY")
BASE_URL = os.getenv("IMEDNET_BASE_URL")

def main():
    """Demonstrates basic client initialization and API calls."""
    if not API_KEY or not SECURITY_KEY or not BASE_URL:
        logging.error(
            "API Key, Security Key, or Base URL not configured. Set IMEDNET_API_KEY, IMEDNET_SECURITY_KEY, and IMEDNET_BASE_URL environment variables."
        )
        return

    try:
        # Initialize the ImednetClient using environment variables
        # The client automatically reads IMEDNET_API_KEY, IMEDNET_SECURITY_KEY,
        # and IMEDNET_BASE_URL if they are set.
        client = ImednetClient(base_url=BASE_URL)
        logging.info("iMednet client initialized successfully.")

        # --- Example 1: List Studies --- 
        logging.info("\n--- Example: Listing Studies ---")
        # Use the studies resource client
        studies_response = client.studies.list_studies(size=5) # Get first 5 studies

        if studies_response and studies_response.data:
            logging.info(f"Successfully retrieved {len(studies_response.data)} studies:")
            first_study_key = None
            for study in studies_response.data:
                logging.info(f"  - Study Name: {study.studyName}, Key: {study.studyKey}")
                if first_study_key is None:
                    first_study_key = study.studyKey # Save the key of the first study for the next example
        else:
            logging.warning("No studies found or API call failed.")
            first_study_key = None # Ensure it's None if no studies found

        # --- Example 2: List Sites for the First Study --- 
        logging.info("\n--- Example: Listing Sites for a Study ---")
        if first_study_key:
            logging.info(f"Fetching sites for study key: {first_study_key}...")
            # Use the sites resource client
            sites_response = client.sites.list_sites(study_key=first_study_key, size=5) # Get first 5 sites

            if sites_response and sites_response.data:
                logging.info(f"Successfully retrieved {len(sites_response.data)} sites:")
                for site in sites_response.data:
                    logging.info(f"  - Site Name: {site.siteName}, ID: {site.siteId}")
            else:
                logging.warning(f"No sites found for study {first_study_key} or API call failed.")
        else:
            logging.info("Skipping site listing as no studies were found in the previous step.")

        # Add more examples as needed, e.g., fetching records, creating records
        # logging.info("\n--- Example: Fetching Records (Add details) ---")
        # try:
        #     records_response = client.records.list_records(study_key="YOUR_STUDY_KEY", filter='subjectKey=="YOUR_SUBJECT_KEY"', size=10)
        #     if records_response and records_response.data:
        #         logging.info(f"Found {len(records_response.data)} records.")
        #     else:
        #         logging.info("No records found for the filter.")
        # except ImednetSdkException as record_err:
        #     logging.error(f"Error fetching records: {record_err}")

    except ImednetSdkException as e:
        logging.error(f"An SDK/API error occurred: {e}")
        logging.error(f"  Status Code: {e.status_code}, API Code: {e.api_error_code}, Details: {e.response_body}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()
