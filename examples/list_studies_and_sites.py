# examples/list_studies_and_sites.py
"""
Example script demonstrating how to list studies and their associated sites
using the iMednet Python SDK.
"""
import os
import logging
from dotenv import load_dotenv
from imednet_sdk import ImednetClient
from imednet_sdk.exceptions import ImednetException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file (optional, for credentials)
# Create a .env file in the same directory with:
# IMEDNET_API_KEY=your_api_key
# IMEDNET_BASE_URL=your_base_url
load_dotenv()

API_KEY = os.getenv("IMEDNET_API_KEY")
BASE_URL = os.getenv("IMEDNET_BASE_URL")

def main():
    """Main function to list studies and sites."""
    if not API_KEY or not BASE_URL:
        logging.error("API Key or Base URL not configured. Set IMEDNET_API_KEY and IMEDNET_BASE_URL environment variables.")
        return

    try:
        # Initialize the client
        client = ImednetClient(base_url=BASE_URL, api_key=API_KEY)
        logging.info("iMednet client initialized successfully.")

        # --- List Studies ---
        logging.info("Fetching studies...")
        # Assumes client.studies.list() returns a list of study objects/dicts
        studies = client.studies.list()

        if not studies:
            logging.warning("No studies found for this account.")
            return

        logging.info(f"Found {len(studies)} studies:")
        for study in studies:
            # Adjust attribute access (e.g., study.study_name or study['studyName']) based on actual SDK model
            study_name = study.get('studyName', 'N/A')
            study_oid = study.get('studyOid', 'N/A')
            logging.info(f"  - Study Name: {study_name}, OID: {study_oid}")

            # --- List Sites for each Study ---
            if study_oid and study_oid != 'N/A':
                logging.info(f"  Fetching sites for study OID: {study_oid}...")
                try:
                    # Assumes client.sites.list() can filter by study_oid
                    sites = client.sites.list(study_oid=study_oid)
                    if sites:
                        logging.info(f"    Found {len(sites)} sites:")
                        for site in sites:
                            # Adjust attribute access based on actual SDK model
                            site_name = site.get('siteName', 'N/A')
                            site_oid = site.get('siteOid', 'N/A')
                            logging.info(f"      - Site Name: {site_name}, OID: {site_oid}")
                    else:
                        logging.info("    No sites found for this study.")
                except ImednetException as site_err:
                    logging.error(f"    Error fetching sites for study {study_oid}: {site_err}")
                except AttributeError:
                    logging.warning(f"    Skipping site listing: client.sites does not seem to have a 'list' method or does not support study_oid filtering.")
            else:
                logging.warning("  Study OID not found or invalid, cannot fetch sites.")

    except ImednetException as e:
        logging.error(f"An API error occurred: {e}")
    except AttributeError as e:
        logging.error(f"An SDK structure error occurred (e.g., client.studies not found): {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
