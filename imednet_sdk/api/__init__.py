"""imednet_sdk.api: Resource-Specific API Clients.

This subpackage contains dedicated client classes for interacting with specific
resource types within the iMednet API (e.g., Studies, Sites, Records, Subjects).

Each client class (e.g., `StudiesClient`, `RecordsClient`) inherits from the
base `ResourceClient` and provides methods tailored to the operations available
for that resource (e.g., `list_studies`, `create_records`). These clients are
accessed via properties on the main `ImednetClient` instance.

Example:
    ```python
    from imednet_sdk import ImednetClient

    client = ImednetClient()
    studies_response = client.studies.list_studies()
    records_response = client.records.list_records(study_key="DEMO")
    ```
"""

from ._base import ResourceClient
from .codings import CodingsClient
from .forms import FormsClient
from .intervals import IntervalsClient
from .jobs import JobsClient
from .queries import QueriesClient
from .record_revisions import RecordRevisionsClient
from .records import RecordsClient
from .sites import SitesClient
from .studies import StudiesClient
from .subjects import SubjectsClient
from .users import UsersClient
from .variables import VariablesClient
from .visits import VisitsClient

__all__ = [
    "ResourceClient",
    "StudiesClient",
    "SitesClient",
    "FormsClient",
    "IntervalsClient",
    "RecordsClient",
    "RecordRevisionsClient",
    "VariablesClient",
    "CodingsClient",
    "SubjectsClient",
    "UsersClient",
    "VisitsClient",
    "JobsClient",
    "QueriesClient",
]
