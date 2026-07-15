"""Endpoints package for the iMedNet SDK.

This package contains all API endpoint implementations for accessing iMedNet resources.
"""

from imednet.endpoints.codings import AsyncCodingsEndpoint, CodingsEndpoint
from imednet.endpoints.forms import AsyncFormsEndpoint, FormsEndpoint
from imednet.endpoints.intervals import AsyncIntervalsEndpoint, IntervalsEndpoint
from imednet.endpoints.jobs import AsyncJobsEndpoint, JobsEndpoint
from imednet.endpoints.queries import AsyncQueriesEndpoint, QueriesEndpoint
from imednet.endpoints.record_revisions import AsyncRecordRevisionsEndpoint, RecordRevisionsEndpoint
from imednet.endpoints.records import AsyncRecordsEndpoint, RecordsEndpoint
from imednet.endpoints.sites import AsyncSitesEndpoint, SitesEndpoint
from imednet.endpoints.studies import AsyncStudiesEndpoint, StudiesEndpoint
from imednet.endpoints.subjects import AsyncSubjectsEndpoint, SubjectsEndpoint
from imednet.endpoints.users import AsyncUsersEndpoint, UsersEndpoint
from imednet.endpoints.variables import AsyncVariablesEndpoint, VariablesEndpoint
from imednet.endpoints.visits import AsyncVisitsEndpoint, VisitsEndpoint

__all__: list[str] = [
    "AsyncCodingsEndpoint",
    "AsyncFormsEndpoint",
    "AsyncIntervalsEndpoint",
    "AsyncJobsEndpoint",
    "AsyncQueriesEndpoint",
    "AsyncRecordRevisionsEndpoint",
    "AsyncRecordsEndpoint",
    "AsyncSitesEndpoint",
    "AsyncStudiesEndpoint",
    "AsyncSubjectsEndpoint",
    "AsyncUsersEndpoint",
    "AsyncVariablesEndpoint",
    "AsyncVisitsEndpoint",
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
