import pytest

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

CASES = [
    (codings.CodingsEndpoint, codings, Coding, "C1"),
    (forms.FormsEndpoint, forms, Form, 1),
    (intervals.IntervalsEndpoint, intervals, Interval, 1),
    (queries.QueriesEndpoint, queries, Query, 1),
    (record_revisions.RecordRevisionsEndpoint, record_revisions, RecordRevision, 1),
    (records.RecordsEndpoint, records, Record, 1),
    (sites.SitesEndpoint, sites, Site, 1),
    (studies.StudiesEndpoint, studies, Study, "S1"),
    (subjects.SubjectsEndpoint, subjects, Subject, "SUB"),
    (users.UsersEndpoint, users, User, 1),
    (variables.VariablesEndpoint, variables, Variable, 1),
    (visits.VisitsEndpoint, visits, Visit, 1),
]


@pytest.mark.parametrize("cls,module,model,item_id", CASES)
def test_list_and_get(dummy_client, context, paginator_factory, cls, module, model, item_id):
    ep = cls(dummy_client, context)
    capture = paginator_factory(module, [{cls._id_param: item_id}])

    list_kwargs = {"study_key": "S1"} if getattr(cls, "requires_study_key", True) else {}
    result = ep.list(**list_kwargs)

    expected_path = "/api/v1/edc/studies"
    if getattr(cls, "requires_study_key", True):
        expected_path += f"/S1/{cls.PATH}"
    elif cls.PATH:
        expected_path += f"/{cls.PATH}"
    assert capture["path"] == expected_path
    assert isinstance(result[0], model)

    get_args = ("S1", item_id) if getattr(cls, "requires_study_key", True) else (None, item_id)
    got = ep.get(*get_args)
    assert isinstance(got, model)


@pytest.mark.asyncio
@pytest.mark.parametrize("cls,module,model,item_id", CASES)
async def test_async_list_and_get(
    dummy_client,
    context,
    async_paginator_factory,
    cls,
    module,
    model,
    item_id,
):
    ep = cls(dummy_client, context, async_client=dummy_client)
    capture = async_paginator_factory(module, [{cls._id_param: item_id}])

    list_kwargs = {"study_key": "S1"} if getattr(cls, "requires_study_key", True) else {}
    result = await ep.async_list(**list_kwargs)

    expected_path = "/api/v1/edc/studies"
    if getattr(cls, "requires_study_key", True):
        expected_path += f"/S1/{cls.PATH}"
    elif cls.PATH:
        expected_path += f"/{cls.PATH}"
    assert capture["path"] == expected_path
    assert isinstance(result[0], model)

    get_args = ("S1", item_id) if getattr(cls, "requires_study_key", True) else (None, item_id)
    got = await ep.async_get(*get_args)
    assert isinstance(got, model)
