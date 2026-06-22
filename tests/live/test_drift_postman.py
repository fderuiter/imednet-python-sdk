"""TODO: Add docstring."""

import logging
import os

import pytest

from imednet.endpoints.registry import ENDPOINT_REGISTRY
from imednet.sdk import ImednetSDK

logger = logging.getLogger(__name__)


def test_postman_collection_drift(sdk: ImednetSDK, study_key: str):
    """Iterates over ENDPOINT_REGISTRY to test all read endpoints
    against live API and validates against SDK internal models.
    """
    os.environ["IMEDNET_STRICT_MODE"] = "1"

    endpoints_to_test = list(ENDPOINT_REGISTRY.keys())
    assert len(endpoints_to_test) > 0, "No endpoints found in registry"

    for endpoint in endpoints_to_test:
        endpoint_cls = ENDPOINT_REGISTRY[endpoint]
        # Some endpoints like jobs don't implement list natively or require special params,
        # but the test checks all endpoints that have a MODEL defined.
        if not hasattr(endpoint_cls, "MODEL"):
            continue

        model_cls = endpoint_cls.MODEL

        # Get instance from sdk
        if not hasattr(sdk, endpoint):
            continue

        endpoint_obj = getattr(sdk, endpoint)

        # Build path using endpoint's PATH
        path = endpoint_cls.PATH

        # Add studyKey if it's required (mostly everything except studies)
        params = {}
        if endpoint != "studies" and endpoint != "jobs":
            params["studyKey"] = study_key

        try:
            response = sdk._client.get(path, params=params)
            response.raise_for_status()
            data = response.json()
            items = data.get("recordData") if "recordData" in data else data.get("data", [])
            for item in items:
                # Validates using the internal model
                model_cls.from_json(item)
        except Exception as e:
            logger.warning(f"Drift detected in {endpoint}: {e}")
            raise
