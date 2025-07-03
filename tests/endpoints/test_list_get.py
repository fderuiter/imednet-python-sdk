import imednet.endpoints.codings as codings
import imednet.endpoints.forms as forms
import imednet.endpoints.intervals as intervals
import imednet.endpoints.queries as queries
import imednet.endpoints.record_revisions as record_revisions
import imednet.endpoints.records as records
import imednet.endpoints.sites as sites
import imednet.endpoints.subjects as subjects
import imednet.endpoints.users as users
import imednet.endpoints.variables as variables
import imednet.endpoints.visits as visits
import pytest

ENDPOINTS = [
    (codings.CodingsEndpoint, "codingId"),
    (forms.FormsEndpoint, "formId"),
    (intervals.IntervalsEndpoint, "intervalId"),
    (queries.QueriesEndpoint, "annotationId"),
    (record_revisions.RecordRevisionsEndpoint, "recordRevisionId"),
    (records.RecordsEndpoint, "recordId"),
    (sites.SitesEndpoint, "siteId"),
    (subjects.SubjectsEndpoint, "subjectKey"),
    (users.UsersEndpoint, "userId"),
    (variables.VariablesEndpoint, "variableId"),
    (visits.VisitsEndpoint, "visitId"),
]


@pytest.mark.parametrize("cls,field", ENDPOINTS)
def test_get_delegates_to_list(monkeypatch, dummy_client, context, cls, field):
    ep = cls(dummy_client, context)
    called = {}

    def fake_list_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        called["study_key"] = study_key
        called["refresh"] = refresh
        called["filters"] = filters
        return [1]

    monkeypatch.setattr(cls, "_list_impl", fake_list_impl)

    res = ep.get("S1", 1)
    assert called["study_key"] == "S1"
    assert called["filters"] == {field: 1}
    assert res == 1
