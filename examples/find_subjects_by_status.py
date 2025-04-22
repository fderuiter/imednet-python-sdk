# examples/find_subjects_by_status.py
"""
Example script demonstrating how to find subjects by their status
within a specific study using the iMednet Python SDK.
"""
import os
import logging
from dotenv import load_dotenv
from imednet_sdk import ImednetClient
from imednet_sdk.exceptions import ImednetException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("IMEDNET_API_KEY")
BASE_URL = os.getenv("IMEDNET_BASE_URL")

# --- Configuration ---
# Specify the Study OID and the desired Subject Status to filter by
TARGET_STUDY_OID = "STUDY_OID_HERE"  # Replace with a valid Study OID from your iMednet instance
TARGET_SUBJECT_STATUS = "Screening"  # Replace with a valid status (e.g., "Enrolled", "Screen Failed", "Completed")
# ---------------------

def main():
    """Main function to find subjects by status."""
    if not API_KEY or not BASE_URL:
        logging.error("API Key or Base URL not configured. Set IMEDNET_API_KEY and IMEDNET_BASE_URL environment variables.")
        return

    if TARGET_STUDY_OID == "STUDY_OID_HERE":
        logging.warning("Please replace 'STUDY_OID_HERE' with an actual Study OID in the script.")
        # Optionally, you could try listing studies first to get an OID, but for a focused example, we require it.
        return

    try:
        # Initialize the client
        client = ImednetClient(base_url=BASE_URL, api_key=API_KEY)
        logging.info("iMednet client initialized successfully.")

        # --- Find Subjects by Status ---
        logging.info(f"Fetching subjects with status '{TARGET_SUBJECT_STATUS}' in study '{TARGET_STUDY_OID}'...")

        # Assumes client.subjects.list() supports filtering by study_oid and status
        # The exact parameter names ('study_oid', 'status') might differ based on the SDK implementation.
        subjects = client.subjects.list(study_oid=TARGET_STUDY_OID, status=TARGET_SUBJECT_STATUS)

        if not subjects:
            logging.warning(f"No subjects found with status '{TARGET_SUBJECT_STATUS}' in study '{TARGET_STUDY_OID}'.")
            return

        logging.info(f"Found {len(subjects)} subjects with status '{TARGET_SUBJECT_STATUS}':")
        for subject in subjects:
            # Adjust attribute access based on the actual SDK model
            subject_key = subject.get('subjectKey', 'N/A') # Or subject.subject_key
            subject_status = subject.get('status', 'N/A') # Or subject.status
            site_oid = subject.get('siteOid', 'N/A')     # Or subject.site_oid
            logging.info(f"  - Subject Key: {subject_key}, Status: {subject_status}, Site OID: {site_oid}")

    except ImednetException as e:
        logging.error(f"An API error occurred: {e}")
    except AttributeError as e:
        logging.error(f"An SDK structure error occurred (e.g., client.subjects.list or filtering parameters might be incorrect): {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
