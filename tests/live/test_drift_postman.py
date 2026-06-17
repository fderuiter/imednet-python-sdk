import json
import logging
import os

import pytest

from imednet.models.codings import Coding
from imednet.models.forms import Form
from imednet.models.intervals import Interval
from imednet.models.queries import Query
from imednet.models.record_revisions import RecordRevision
from imednet.models.records import Record
from imednet.models.sites import Site
from imednet.models.studies import Study
from imednet.models.subjects import Subject
from imednet.models.users import User
from imednet.models.variables import Variable
from imednet.models.visits import Visit
from imednet.sdk import ImednetSDK

logger = logging.getLogger(__name__)

MODEL_MAP = {
    "studies": Study,
    "forms": Form,
    "intervals": Interval,
    "queries": Query,
    "records": Record,
    "record_revisions": RecordRevision,
    "sites": Site,
    "subjects": Subject,
    "users": User,
    "variables": Variable,
    "visits": Visit,
    "codings": Coding,
}


def test_postman_collection_drift(sdk: ImednetSDK, study_key: str):
    """
    Reads the Postman collection, identifies API endpoints,
    and compares the live API responses against the SDK's internal models.
    """
    os.environ["IMEDNET_STRICT_MODE"] = "1"

    if "IMEDNET_POSTMAN_PATH" in os.environ:
        collection_path = os.environ["IMEDNET_POSTMAN_PATH"]
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        collection_path = "/app/imednet.postman_collection.json"
        while current_dir != os.path.dirname(current_dir):
            candidate = os.path.join(current_dir, "imednet.postman_collection.json")
            if os.path.exists(candidate):
                collection_path = candidate
                break
            current_dir = os.path.dirname(current_dir)

    if not os.path.exists(collection_path):
        pytest.skip("Postman collection not found")

    with open(collection_path, 'r') as f:
        data = json.load(f)

    # Walk the collection to find endpoints
    endpoints_to_test = set()

    def walk(items):
        for item in items:
            if "item" in item:
                walk(item["item"])
            elif "request" in item:
                req = item["request"]
                if "url" in req and "path" in req["url"]:
                    path = req["url"]["path"]
                    # Usually paths are like ['api', 'v1', 'studies'] or ['studies']
                    for p in path:
                        if p in MODEL_MAP:
                            endpoints_to_test.add(p)

    walk(data.get("item", []))

    assert len(endpoints_to_test) > 0, "No endpoints found in Postman collection"

    for endpoint in endpoints_to_test:
        model_cls = MODEL_MAP[endpoint]

        # Build URL. The SDK handles base_url and auth.
        url = f"/{endpoint}"
        if endpoint != "studies":
            url += f"?studyKey={study_key}"

        try:
            response = sdk._client.get(url)
            data = response.json()
            items = data.get("data", [])
            for item in items:
                # Validates using the internal model
                model_cls.from_json(item)
        except Exception as e:
            logger.warning(f"Drift detected in {endpoint}: {e}")
            raise
