import imednet.endpoints.codings as codings
import imednet.endpoints.forms as forms
import imednet.endpoints.intervals as intervals
import imednet.endpoints.queries as queries
import imednet.endpoints.record_revisions as record_revisions
import imednet.endpoints.records as records
import imednet.endpoints.sites as sites
import imednet.endpoints.studies as studies
import imednet.endpoints.subjects as subjects
import imednet.endpoints.users as users
import imednet.endpoints.variables as variables
import imednet.endpoints.visits as visits
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

ENDPOINTS = [
    (forms.FormsEndpoint, forms, Form, 1),
    (codings.CodingsEndpoint, codings, Coding, "1"),
    (intervals.IntervalsEndpoint, intervals, Interval, 1),
    (queries.QueriesEndpoint, queries, Query, 1),
    (record_revisions.RecordRevisionsEndpoint, record_revisions, RecordRevision, 1),
    (records.RecordsEndpoint, records, Record, 1),
    (sites.SitesEndpoint, sites, Site, 1),
    (studies.StudiesEndpoint, studies, Study, "S1"),
    (subjects.SubjectsEndpoint, subjects, Subject, "X"),
    (users.UsersEndpoint, users, User, 1),
    (variables.VariablesEndpoint, variables, Variable, 1),
    (visits.VisitsEndpoint, visits, Visit, 1),
]


@pytest.mark.parametrize("cls,module,model,item_id", ENDPOINTS)
def test_list_and_get(
    cls, module, model, item_id, dummy_client, context, paginator_factory, monkeypatch
):
    ep = cls(dummy_client, context)
    capture = paginator_factory(module, [{cls._id_param: item_id}])

    list_kwargs = {"study_key": "S1"} if getattr(cls, "requires_study_key", True) else {}
    if cls is users.UsersEndpoint:
        list_kwargs["include_inactive"] = True
    result = ep.list(**list_kwargs)

    expected = (
        ep._build_path("S1", cls.PATH)
        if getattr(cls, "requires_study_key", True)
        else ep._build_path(cls.PATH)
    )
    assert capture["path"] == expected
    assert isinstance(result[0], model)

    called = {}

    def fake_list(self, client, paginator_cls, *, study_key=None, refresh=False, **filters):
        called["study_key"] = study_key
        called["refresh"] = refresh
        called["filters"] = filters
        return [model()]

    monkeypatch.setattr(cls, "_list_impl", fake_list)

    if getattr(cls, "requires_study_key", True):
        res = ep.get("S1", item_id)
    else:
        res = ep.get(item_id)

    assert called["refresh"] is True
    assert called["filters"] == {cls._id_param: item_id}
    assert isinstance(res, model)
