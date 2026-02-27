"""
Registry for all available API endpoints.

This module decouples the endpoint implementations from the main SDK class,
allowing for easier extension and maintenance.
"""

from __future__ import annotations

from typing import Dict, Type

from imednet.core.endpoint.base import GenericEndpoint
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

ENDPOINT_REGISTRY: Dict[str, Type[GenericEndpoint]] = {
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
