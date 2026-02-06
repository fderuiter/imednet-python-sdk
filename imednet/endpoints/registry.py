"""
Registry of all available API endpoints.

This module decouples endpoint registration from the main SDK entry point,
preventing circular imports and allowing for easier inspection.
"""

from typing import Dict, Type

from imednet.endpoints.base import BaseEndpoint
from imednet.endpoints.codings import CodingsEndpoint
from imednet.endpoints.forms import FormsEndpoint
from imednet.endpoints.intervals import IntervalsEndpoint
from imednet.endpoints.jobs import JobsEndpoint
from imednet.endpoints.queries import QueriesEndpoint
from imednet.endpoints.record_revisions import RecordRevisionsEndpoint
from imednet.endpoints.records import RecordsEndpoint
from imednet.endpoints.sites import SitesEndpoint
from imednet.endpoints.studies import StudiesEndpoint
from imednet.endpoints.subjects import SubjectsEndpoint
from imednet.endpoints.users import UsersEndpoint
from imednet.endpoints.variables import VariablesEndpoint
from imednet.endpoints.visits import VisitsEndpoint

# Mapping of attribute names to their endpoint classes
ENDPOINT_REGISTRY: Dict[str, Type[BaseEndpoint]] = {
    "codings": CodingsEndpoint,
    "forms": FormsEndpoint,
    "intervals": IntervalsEndpoint,
    "jobs": JobsEndpoint,
    "queries": QueriesEndpoint,
    "record_revisions": RecordRevisionsEndpoint,
    "records": RecordsEndpoint,
    "sites": SitesEndpoint,
    "studies": StudiesEndpoint,
    "subjects": SubjectsEndpoint,
    "users": UsersEndpoint,
    "variables": VariablesEndpoint,
    "visits": VisitsEndpoint,
}
