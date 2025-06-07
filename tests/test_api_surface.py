import inspect

from imednet.async_sdk import AsyncImednetSDK
from imednet.endpoints import (
    async_codings,
    async_forms,
    async_intervals,
    async_jobs,
    async_queries,
    async_record_revisions,
    async_records,
    async_sites,
    async_studies,
    async_subjects,
    async_users,
    async_variables,
    async_visits,
    codings,
    forms,
    intervals,
    jobs,
    queries,
    record_revisions,
    records,
    sites,
    studies,
    subjects,
    users,
    variables,
    visits,
)
from imednet.sdk import ImednetSDK


def public_attrs(cls: type) -> set[str]:
    return {name for name, _ in inspect.getmembers(cls) if not name.startswith("_")}


def test_sdk_api_surface():
    sync_public = public_attrs(ImednetSDK)
    async_public = public_attrs(AsyncImednetSDK)

    sync_public -= {"close", "set_default_study", "clear_default_study"}
    async_public -= {"aclose"}

    assert sync_public == async_public


ENDPOINT_PAIRS = [
    (codings.CodingsEndpoint, async_codings.AsyncCodingsEndpoint),
    (forms.FormsEndpoint, async_forms.AsyncFormsEndpoint),
    (intervals.IntervalsEndpoint, async_intervals.AsyncIntervalsEndpoint),
    (jobs.JobsEndpoint, async_jobs.AsyncJobsEndpoint),
    (queries.QueriesEndpoint, async_queries.AsyncQueriesEndpoint),
    (record_revisions.RecordRevisionsEndpoint, async_record_revisions.AsyncRecordRevisionsEndpoint),
    (records.RecordsEndpoint, async_records.AsyncRecordsEndpoint),
    (sites.SitesEndpoint, async_sites.AsyncSitesEndpoint),
    (studies.StudiesEndpoint, async_studies.AsyncStudiesEndpoint),
    (subjects.SubjectsEndpoint, async_subjects.AsyncSubjectsEndpoint),
    (users.UsersEndpoint, async_users.AsyncUsersEndpoint),
    (variables.VariablesEndpoint, async_variables.AsyncVariablesEndpoint),
    (visits.VisitsEndpoint, async_visits.AsyncVisitsEndpoint),
]


def test_endpoint_api_surface():
    for sync_cls, async_cls in ENDPOINT_PAIRS:
        assert public_attrs(sync_cls) == public_attrs(async_cls)
