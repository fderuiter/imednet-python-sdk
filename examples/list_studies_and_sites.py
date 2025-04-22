# examples/list_studies_and_sites.py
"""
Example: Listing Studies and Their Sites via iMednet API.

This script demonstrates how to use the `imednet-python-sdk` to:
1. Retrieve a list of all studies accessible to the authenticated user.
2. For each study found, retrieve a list of its associated sites.

**Prerequisites:**

1.  **Install SDK:** `pip install imednet-sdk python-dotenv`
2.  **Environment Variables:** Create a `.env` file in the same directory
    with your iMednet API key, security key, and base URL:
    ```
    IMEDNET_API_KEY="your_api_key_here"
    IMEDNET_SECURITY_KEY="your_security_key_here"
    IMEDNET_BASE_URL="https://your_imednet_instance.imednetapi.com"
    ```

**Usage:**

```bash
python examples/list_studies_and_sites.py
```

The script will query the API, list the studies, and then list the sites for each study.
It handles potential pagination for studies and sites if necessary (though this example
fetches only the first page by default).
"""

import logging
import os

from dotenv import load_dotenv

from imednet_sdk import ImednetClient
from imednet_sdk.exceptions import ImednetSdkException

# examples/list_studies_and_sites.py
"""
Example script demonstrating how to list studies and their associated sites
using the iMednet Python SDK.

This script assumes:
- You have a .env file in the same directory with IMEDNET_API_KEY and
  IMEDNET_BASE_URL defined, or these are set as environment variables.
- The SDK client has methods like `client.studies.list()` and
  `client.sites.list(study_oid=...)`.
- Study and Site objects/dictionaries returned by the SDK have keys like
  'studyName', 'studyOid', 'siteName', 'siteOid'. Adjust access as needed.
"""

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables from .env file (optional, for credentials)
# Create a .env file in the same directory with:
# IMEDNET_API_KEY=your_api_key
# IMEDNET_BASE_URL=your_base_url
load_dotenv()

API_KEY = os.getenv("IMEDNET_API_KEY")
SECURITY_KEY = os.getenv("IMEDNET_SECURITY_KEY")  # Added security key
BASE_URL = os.getenv("IMEDNET_BASE_URL")


def main():
    """Initializes the client, lists studies, and then lists sites for each study."""
    if not API_KEY or not SECURITY_KEY or not BASE_URL:
        logging.error(
            "API Key, Security Key, or Base URL not configured. Set IMEDNET_API_KEY, "
            "IMEDNET_SECURITY_KEY, and IMEDNET_BASE_URL environment variables."
        )
        return

    try:
        # Initialize the client (using environment variables)
        client = ImednetClient(base_url=BASE_URL)
        logging.info("iMednet client initialized successfully.")

        # --- List Studies ---
        logging.info("Fetching studies...")
        # Use list_studies, which returns an ApiResponse
        studies_response = client.studies.list_studies(size=100)  # Fetch up to 100 studies

        if not studies_response or not studies_response.data:
            logging.warning("No studies found for this account or API call failed.")
            return

        studies = studies_response.data
        logging.info(f"Found {len(studies)} studies (on first page):")

        # Handle study pagination if needed
        if studies_response.pagination and studies_response.pagination.totalPages > 1:
            logging.info(
                f"  Note: More study pages available (Total: "
                f"{studies_response.pagination.totalPages}). Fetching only the first page."
            )

        for study in studies:
            # Access attributes from the StudyModel
            study_name = study.studyName
            study_key = study.studyKey
            logging.info(f"\n-- Study: {study_name} (Key: {study_key}) --")

            # --- List Sites for each Study ---
            if study_key:
                logging.info(f"  Fetching sites for study key: {study_key}...")
                try:
                    # Use list_sites with study_key
                    sites_response = client.sites.list_sites(
                        study_key=study_key, size=100
                    )  # Fetch up to 100 sites

                    if sites_response and sites_response.data:
                        sites = sites_response.data
                        logging.info(f"    Found {len(sites)} sites (on first page):")
                        for site in sites:
                            # Access attributes from the SiteModel
                            site_name = site.siteName
                            site_id = site.siteId
                            logging.info(f"      - Site Name: {site_name}, ID: {site_id}")

                        # Handle site pagination if needed
                        if sites_response.pagination and sites_response.pagination.totalPages > 1:
                            logging.info(
                                f"      Note: More site pages available (Total: "
                                f"{sites_response.pagination.totalPages}). "
                                f"Fetching only the first page."
                            )

                    else:
                        logging.info("    No sites found for this study.")
                except ImednetSdkException as site_err:
                    logging.error(f"    Error fetching sites for study {study_key}: {site_err}")
                    logging.error(
                        f"      Status Code: {site_err.status_code}, "
                        f"API Code: {site_err.api_error_code}, "
                        f"Details: {site_err.response_body}"
                    )
                except Exception as site_err:
                    logging.error(
                        f"    An unexpected error occurred fetching sites for study {study_key}: "
                        f"{site_err}",
                        exc_info=True,
                    )
            else:
                logging.warning("  Study Key not found or invalid, cannot fetch sites.")

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
