import asyncio
import pytest

from imednet.core.client import Client
from imednet.core.context import Context
from imednet.endpoints.studies import StudiesEndpoint


@pytest.fixture
def base_url() -> str:
    return "https://api.test"


@pytest.fixture
def client(base_url: str, respx_mock) -> Client:
    return Client(api_key="key", security_key="sec", base_url=base_url)


@pytest.fixture
def context() -> Context:
    return Context()


@pytest.fixture
def studies_endpoint(client: Client, context: Context) -> StudiesEndpoint:
    return StudiesEndpoint(client, context)


@pytest.fixture
def study_json() -> dict:
    return {
        "sponsorKey": "SP",
        "studyKey": "STUDY1",
        "studyId": 1,
        "studyName": "Demo",
        "studyDescription": "desc",
        "studyType": "type",
        "dateCreated": "2024-01-01T00:00:00Z",
        "dateModified": "2024-01-02T00:00:00Z",
    }


@pytest.fixture
async def async_studies(studies_endpoint: StudiesEndpoint) -> list:
    # Wrapper to call synchronous list in a thread for async tests
    return await asyncio.to_thread(studies_endpoint.list)
