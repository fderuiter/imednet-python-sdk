"""
Endpoints package for the iMedNet SDK.

This package contains all API endpoint implementations for accessing iMedNet resources.
"""

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

__all__: list[str] = [
    "CodingsEndpoint",
    "FormsEndpoint",
    "IntervalsEndpoint",
    "JobsEndpoint",
    "QueriesEndpoint",
    "RecordRevisionsEndpoint",
    "RecordsEndpoint",
    "SitesEndpoint",
    "StudiesEndpoint",
    "SubjectsEndpoint",
    "UsersEndpoint",
    "VariablesEndpoint",
    "VisitsEndpoint",
]
