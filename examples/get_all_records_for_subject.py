# examples/get_all_records_for_subject.py
"""
Example script demonstrating how to retrieve all records for a specific subject,
automatically handling pagination using the iMednet Python SDK's iterator feature.
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
# Specify the Study OID and Subject Key for which to retrieve records
TARGET_STUDY_OID = "STUDY_OID_HERE"  # Replace with a valid Study OID
TARGET_SUBJECT_KEY = "SUBJECT_KEY_HERE" # Replace with a valid Subject Key
# ---------------------

def main():
    """Main function to get all records for a subject using pagination."""
    if not API_KEY or not BASE_URL:
        logging.error("API Key or Base URL not configured. Set IMEDNET_API_KEY and IMEDNET_BASE_URL environment variables.")
        return

    if TARGET_STUDY_OID == "STUDY_OID_HERE" or TARGET_SUBJECT_KEY == "SUBJECT_KEY_HERE":
        logging.warning("Please replace 'STUDY_OID_HERE' and 'SUBJECT_KEY_HERE' with actual values in the script.")
        return

    try:
        # Initialize the client
        client = ImednetClient(base_url=BASE_URL, api_key=API_KEY)
        logging.info("iMednet client initialized successfully.")

        # --- Get All Records for Subject (with Pagination) ---
        logging.info(f"Fetching all records for subject '{TARGET_SUBJECT_KEY}' in study '{TARGET_STUDY_OID}'...")

        all_records = []
        record_count = 0

        # Assumes client.records.list_all() returns an iterator that handles pagination.
        # It should accept study_oid and subject_key as filters.
        # If list_all doesn't exist, you might need manual pagination:
        # page = 1
        # while True:
        #     records_page = client.records.list(study_oid=..., subject_key=..., page=page, limit=100) # Adjust params
        #     if not records_page:
        #         break
        #     all_records.extend(records_page)
        #     page += 1

        try:
            # Use the SDK's pagination helper if available (preferred)
            record_iterator = client.records.list_all(study_oid=TARGET_STUDY_OID, subject_key=TARGET_SUBJECT_KEY)

            for record in record_iterator:
                record_count += 1
                all_records.append(record)
                # Process each record as needed
                form_oid = record.get('formOid', 'N/A')
                record_id = record.get('id', 'N/A')
                logging.debug(f"  Retrieved record ID: {record_id}, Form OID: {form_oid}") # Use DEBUG level for potentially many records

            if not all_records:
                logging.warning(f"No records found for subject '{TARGET_SUBJECT_KEY}' in study '{TARGET_STUDY_OID}'.")
            else:
                logging.info(f"Successfully retrieved {record_count} records in total for subject '{TARGET_SUBJECT_KEY}'.")
                # You can now work with the `all_records` list
                # logging.info(f"First record details: {all_records[0]}")

        except AttributeError:
            logging.error("SDK Error: client.records does not seem to have a 'list_all' method for automatic pagination, or the filtering parameters are incorrect. Manual pagination might be required.")
        except ImednetException as e:
            logging.error(f"An API error occurred during record fetching: {e}")

    except ImednetException as e:
        logging.error(f"An API error occurred during client initialization: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
