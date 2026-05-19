"""
Registry for all available API endpoints.

This module decouples the endpoint implementations from the main SDK class,
allowing for easier extension and maintenance.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping, Type

from imednet.core.endpoint.base import GenericEndpoint
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

ENDPOINT_REGISTRY: Mapping[str, Type[GenericEndpoint]] = MappingProxyType(
    {
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
)

ASYNC_ENDPOINT_REGISTRY: Mapping[str, Type[GenericEndpoint]] = MappingProxyType(
    {
        "codings": AsyncCodingsEndpoint,
        "forms": AsyncFormsEndpoint,
        "intervals": AsyncIntervalsEndpoint,
        "jobs": AsyncJobsEndpoint,
        "queries": AsyncQueriesEndpoint,
        "record_revisions": AsyncRecordRevisionsEndpoint,
        "records": AsyncRecordsEndpoint,
        "sites": AsyncSitesEndpoint,
        "studies": AsyncStudiesEndpoint,
        "subjects": AsyncSubjectsEndpoint,
        "users": AsyncUsersEndpoint,
        "variables": AsyncVariablesEndpoint,
        "visits": AsyncVisitsEndpoint,
    }
)
