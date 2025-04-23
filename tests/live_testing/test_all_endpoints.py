"""
Live testing script for all iMednet SDK endpoints.

This script tests all available endpoints in the iMednet SDK using actual API credentials.
It can be run to validate that the SDK is working correctly with your API keys.

Usage:
    python -m tests.live_testing.test_all_endpoints

Environment variables required:
    - IMEDNET_API_KEY: Your iMednet API key
    - IMEDNET_SECURITY_KEY: Your iMednet security key
    - IMEDNET_BASE_URL: (Optional) Base URL for the API
"""

import argparse
import logging
import sys
from typing import Any, Optional

from imednet_sdk.exceptions import ImednetSdkException

from tests.live_testing.utils import initialize_imednet_client, log_response

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_studies_endpoint(client) -> Optional[str]:
    """
    Test the studies endpoint.

    Returns:
        Optional[str]: First study key found, or None if no studies
    """
    logger.info("\n=== Testing Studies Endpoint ===")
    try:
        studies_response = client.studies.list_studies(size=5)

        if studies_response and studies_response.data:
            log_response(studies_response, "Studies")
            first_study = studies_response.data[0]
            logger.info(f"First study: {first_study.studyName} (Key: {first_study.studyKey})")
            return first_study.studyKey
        else:
            logger.warning("No studies found or API call failed.")
            return None
    except ImednetSdkException as e:
        logger.error(f"API error testing studies endpoint: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error testing studies endpoint: {e}", exc_info=True)
        return None


def test_sites_endpoint(client, study_key: str) -> Optional[int]:
    """
    Test the sites endpoint.

    Args:
        client: Initialized iMednet client
        study_key: Study key to use for testing

    Returns:
        Optional[int]: First site ID found, or None if no sites
    """
    logger.info(f"\n=== Testing Sites Endpoint for Study {study_key} ===")
    try:
        sites_response = client.sites.list_sites(study_key=study_key, size=5)

        if sites_response and sites_response.data:
            log_response(sites_response, "Sites")
            first_site = sites_response.data[0]
            logger.info(f"First site: {first_site.siteName} (ID: {first_site.siteId})")
            return first_site.siteId
        else:
            logger.warning("No sites found or API call failed.")
            return None
    except ImednetSdkException as e:
        logger.error(f"API error testing sites endpoint: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error testing sites endpoint: {e}", exc_info=True)
        return None


def test_subjects_endpoint(client, study_key: str) -> Optional[str]:
    """
    Test the subjects endpoint.

    Args:
        client: Initialized iMednet client
        study_key: Study key to use for testing

    Returns:
        Optional[str]: First subject key found, or None if no subjects
    """
    logger.info(f"\n=== Testing Subjects Endpoint for Study {study_key} ===")
    try:
        subjects_response = client.subjects.list_subjects(study_key=study_key, size=5)

        if subjects_response and subjects_response.data:
            log_response(subjects_response, "Subjects")
            first_subject = subjects_response.data[0]
            logger.info(
                f"First subject: {first_subject.subjectKey} (ID: {first_subject.subjectId})"
            )
            return first_subject.subjectKey
        else:
            logger.warning("No subjects found or API call failed.")
            return None
    except ImednetSdkException as e:
        logger.error(f"API error testing subjects endpoint: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error testing subjects endpoint: {e}", exc_info=True)
        return None


def test_forms_endpoint(client, study_key: str) -> Optional[int]:
    """
    Test the forms endpoint.

    Args:
        client: Initialized iMednet client
        study_key: Study key to use for testing

    Returns:
        Optional[int]: First form ID found, or None if no forms
    """
    logger.info(f"\n=== Testing Forms Endpoint for Study {study_key} ===")
    try:
        forms_response = client.forms.list_forms(study_key=study_key, size=5)

        if forms_response and forms_response.data:
            log_response(forms_response, "Forms")
            first_form = forms_response.data[0]
            logger.info(
                f"First form: {first_form.formName} "
                f"(ID: {first_form.formId}, "
                f"Key: {first_form.formKey})"
            )
            return first_form.formId
        else:
            logger.warning("No forms found or API call failed.")
            return None
    except ImednetSdkException as e:
        logger.error(f"API error testing forms endpoint: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error testing forms endpoint: {e}", exc_info=True)
        return None


def test_intervals_endpoint(client, study_key: str) -> Optional[int]:
    """
    Test the intervals endpoint.

    Args:
        client: Initialized iMednet client
        study_key: Study key to use for testing

    Returns:
        Optional[int]: First interval ID found, or None if no intervals
    """
    logger.info(f"\n=== Testing Intervals Endpoint for Study {study_key} ===")
    try:
        intervals_response = client.intervals.list_intervals(study_key=study_key, size=5)

        if intervals_response and intervals_response.data:
            log_response(intervals_response, "Intervals")
            first_interval = intervals_response.data[0]
            logger.info(
                f"First interval: {first_interval.intervalName} (ID: {first_interval.intervalId})"
            )
            return first_interval.intervalId
        else:
            logger.warning("No intervals found or API call failed.")
            return None
    except ImednetSdkException as e:
        logger.error(f"API error testing intervals endpoint: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error testing intervals endpoint: {e}", exc_info=True)
        return None


def test_variables_endpoint(client, study_key: str, form_id: Optional[int] = None) -> None:
    """
    Test the variables endpoint.

    Args:
        client: Initialized iMednet client
        study_key: Study key to use for testing
        form_id: Optional form ID to filter variables
    """
    logger.info(f"\n=== Testing Variables Endpoint for Study {study_key} ===")
    try:
        # Build filter if form_id is provided
        kwargs: dict[str, Any] = {"size": 5}
        if form_id:
            kwargs["filter"] = f"formId=={form_id}"

        variables_response = client.variables.list_variables(study_key=study_key, **kwargs)

        if variables_response and variables_response.data:
            log_response(variables_response, "Variables")
            first_variable = variables_response.data[0]
            logger.info(
                f"First variable: {first_variable.variableKey} (ID: {first_variable.variableId})"
            )
        else:
            logger.warning("No variables found or API call failed.")
    except ImednetSdkException as e:
        logger.error(f"API error testing variables endpoint: {e}")
    except Exception as e:
        logger.error(f"Unexpected error testing variables endpoint: {e}", exc_info=True)


def test_records_endpoint(client, study_key: str, form_id: Optional[int] = None) -> Optional[int]:
    """
    Test the records endpoint.

    Args:
        client: Initialized iMednet client
        study_key: Study key to use for testing
        form_id: Optional form ID to filter records

    Returns:
        Optional[int]: First record ID found, or None if no records
    """
    logger.info(f"\n=== Testing Records Endpoint for Study {study_key} ===")
    try:
        # Build filter if form_id is provided
        kwargs: dict[str, Any] = {"size": 5}
        if form_id:
            kwargs["filter"] = f"formId=={form_id}"

        records_response = client.records.list_records(study_key=study_key, **kwargs)

        if records_response and records_response.data:
            log_response(records_response, "Records")
            first_record = records_response.data[0]
            logger.info(f"First record ID: {first_record.recordId}")
            return first_record.recordId
        else:
            logger.warning("No records found or API call failed.")
            return None
    except ImednetSdkException as e:
        logger.error(f"API error testing records endpoint: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error testing records endpoint: {e}", exc_info=True)
        return None


def test_record_revisions_endpoint(client, study_key: str) -> None:
    """
    Test the record revisions endpoint.

    Args:
        client: Initialized iMednet client
        study_key: Study key to use for testing
    """
    logger.info(f"\n=== Testing Record Revisions Endpoint for Study {study_key} ===")
    try:
        revisions_response = client.record_revisions.list_record_revisions(
            study_key=study_key, size=5
        )

        if revisions_response and revisions_response.data:
            log_response(revisions_response, "Record Revisions")
            first_revision = revisions_response.data[0]
            logger.info(f"First revision ID: {first_revision.recordRevisionId}")
        else:
            logger.warning("No record revisions found or API call failed.")
    except ImednetSdkException as e:
        logger.error(f"API error testing record revisions endpoint: {e}")
    except Exception as e:
        logger.error(f"Unexpected error testing record revisions endpoint: {e}", exc_info=True)


def test_visits_endpoint(client, study_key: str) -> None:
    """
    Test the visits endpoint.

    Args:
        client: Initialized iMednet client
        study_key: Study key to use for testing
    """
    logger.info(f"\n=== Testing Visits Endpoint for Study {study_key} ===")
    try:
        visits_response = client.visits.list_visits(study_key=study_key, size=5)

        if visits_response and visits_response.data:
            log_response(visits_response, "Visits")
            first_visit = visits_response.data[0]
            logger.info(f"First visit ID: {first_visit.visitId}")
        else:
            logger.warning("No visits found or API call failed.")
    except ImednetSdkException as e:
        logger.error(f"API error testing visits endpoint: {e}")
    except Exception as e:
        logger.error(f"Unexpected error testing visits endpoint: {e}", exc_info=True)


def test_users_endpoint(client, study_key: str) -> None:
    """
    Test the users endpoint.

    Args:
        client: Initialized iMednet client
        study_key: Study key to use for testing
    """
    logger.info(f"\n=== Testing Users Endpoint for Study {study_key} ===")
    try:
        users_response = client.users.list_users(study_key=study_key, size=5)

        if users_response and users_response.data:
            log_response(users_response, "Users")
            first_user = users_response.data[0]
            logger.info(
                f"First user: {first_user.firstName} {first_user.lastName}"
                f" (Login: {first_user.login})"
            )
        else:
            logger.warning("No users found or API call failed.")
    except ImednetSdkException as e:
        logger.error(f"API error testing users endpoint: {e}")
    except Exception as e:
        logger.error(f"Unexpected error testing users endpoint: {e}", exc_info=True)


def test_queries_endpoint(client, study_key: str) -> None:
    """
    Test the queries endpoint.

    Args:
        client: Initialized iMednet client
        study_key: Study key to use for testing
    """
    logger.info(f"\n=== Testing Queries Endpoint for Study {study_key} ===")
    try:
        queries_response = client.queries.list_queries(study_key=study_key, size=5)

        if queries_response and queries_response.data:
            log_response(queries_response, "Queries")
            first_query = queries_response.data[0]
            logger.info(
                f"First query ID: {first_query.annotationId}, "
                f"Description: {first_query.description}"
            )
        else:
            logger.warning("No queries found or API call failed.")
    except ImednetSdkException as e:
        logger.error(f"API error testing queries endpoint: {e}")
    except Exception as e:
        logger.error(f"Unexpected error testing queries endpoint: {e}", exc_info=True)


def test_codings_endpoint(client, study_key: str) -> None:
    """
    Test the codings endpoint.

    Args:
        client: Initialized iMednet client
        study_key: Study key to use for testing
    """
    logger.info(f"\n=== Testing Codings Endpoint for Study {study_key} ===")
    try:
        codings_response = client.codings.list_codings(study_key=study_key, size=5)

        if codings_response and codings_response.data:
            log_response(codings_response, "Codings")
            first_coding = codings_response.data[0]
            logger.info(f"First coding: {first_coding.codingName} (ID: {first_coding.codingId})")
        else:
            logger.warning("No codings found or API call failed.")
    except ImednetSdkException as e:
        logger.error(f"API error testing codings endpoint: {e}")
    except Exception as e:
        logger.error(f"Unexpected error testing codings endpoint: {e}", exc_info=True)


def run_all_tests():
    """Run tests for all endpoints."""
    try:
        # Initialize client
        client = initialize_imednet_client()

        # Start with studies endpoint to get a study key for other endpoints
        study_key = test_studies_endpoint(client)

        if not study_key:
            logger.error("Failed to get a valid study key. Cannot proceed with other tests.")
            return

        # Test sites endpoint
        test_sites_endpoint(client, study_key)

        # Test subjects endpoint
        test_subjects_endpoint(client, study_key)

        # Test forms endpoint
        form_id = test_forms_endpoint(client, study_key)

        # Test intervals endpoint
        test_intervals_endpoint(client, study_key)

        # Test variables endpoint (optionally filtered by form)
        test_variables_endpoint(client, study_key, form_id)

        # Test records endpoint (optionally filtered by form)
        test_records_endpoint(client, study_key, form_id)

        # Test record revisions endpoint
        test_record_revisions_endpoint(client, study_key)

        # Test visits endpoint
        test_visits_endpoint(client, study_key)

        # Test users endpoint
        test_users_endpoint(client, study_key)

        # Test queries endpoint
        test_queries_endpoint(client, study_key)

        # Test codings endpoint
        test_codings_endpoint(client, study_key)

        logger.info("\n=== All Tests Completed ===")

    except Exception as e:
        logger.error(f"Unexpected error during testing: {e}", exc_info=True)


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(description="Test all iMednet SDK endpoints")
    parser.add_argument("--study", help="Specify a study key to use for testing")

    parser.parse_args()

    # Run all tests
    run_all_tests()

    return 0


if __name__ == "__main__":
    sys.exit(main())
