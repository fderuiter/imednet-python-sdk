from imednet.endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY
"""Unit tests for list get."""

import pytest

class Dummy:
    pass
codings = Dummy()
codings.__name__ = 'imednet.endpoints.codings'
class Dummy:
    pass
forms = Dummy()
forms.__name__ = 'imednet.endpoints.forms'
class Dummy:
    pass
intervals = Dummy()
intervals.__name__ = 'imednet.endpoints.intervals'
class Dummy:
    pass
queries = Dummy()
queries.__name__ = 'imednet.endpoints.queries'
class Dummy:
    pass
record_revisions = Dummy()
record_revisions.__name__ = 'imednet.endpoints.record_revisions'
class Dummy:
    pass
records = Dummy()
records.__name__ = 'imednet.endpoints.records'
class Dummy:
    pass
sites = Dummy()
sites.__name__ = 'imednet.endpoints.sites'
class Dummy:
    pass
studies = Dummy()
studies.__name__ = 'imednet.endpoints.studies'
class Dummy:
    pass
subjects = Dummy()
subjects.__name__ = 'imednet.endpoints.subjects'
class Dummy:
    pass
users = Dummy()
users.__name__ = 'imednet.endpoints.users'
class Dummy:
    pass
variables = Dummy()
variables.__name__ = 'imednet.endpoints.variables'
class Dummy:
    pass
visits = Dummy()
visits.__name__ = 'imednet.endpoints.visits'
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
    (ENDPOINT_REGISTRY['codings'], codings, Coding, "C1"),
    (ENDPOINT_REGISTRY['forms'], forms, Form, 1),
    (ENDPOINT_REGISTRY['intervals'], intervals, Interval, 1),
    (ENDPOINT_REGISTRY['queries'], queries, Query, 1),
    (ENDPOINT_REGISTRY['record_revisions'], record_revisions, RecordRevision, 1),
    (ENDPOINT_REGISTRY['records'], records, Record, 1),
    (ENDPOINT_REGISTRY['sites'], sites, Site, 1),
    (ENDPOINT_REGISTRY['studies'], studies, Study, "S1"),
    (ENDPOINT_REGISTRY['subjects'], subjects, Subject, "SUB"),
    (ENDPOINT_REGISTRY['users'], users, User, 1),
    (ENDPOINT_REGISTRY['variables'], variables, Variable, 1),
    (ENDPOINT_REGISTRY['visits'], visits, Visit, 1),
]

ASYNC_CASES = [
    (ASYNC_ENDPOINT_REGISTRY['codings'], codings, Coding, "C1"),
    (ASYNC_ENDPOINT_REGISTRY['forms'], forms, Form, 1),
    (ASYNC_ENDPOINT_REGISTRY['intervals'], intervals, Interval, 1),
    (ASYNC_ENDPOINT_REGISTRY['queries'], queries, Query, 1),
    (ASYNC_ENDPOINT_REGISTRY['record_revisions'], record_revisions, RecordRevision, 1),
    (ASYNC_ENDPOINT_REGISTRY['records'], records, Record, 1),
    (ASYNC_ENDPOINT_REGISTRY['sites'], sites, Site, 1),
    (ASYNC_ENDPOINT_REGISTRY['studies'], studies, Study, "S1"),
    (ASYNC_ENDPOINT_REGISTRY['subjects'], subjects, Subject, "SUB"),
    (ASYNC_ENDPOINT_REGISTRY['users'], users, User, 1),
    (ASYNC_ENDPOINT_REGISTRY['variables'], variables, Variable, 1),
    (ASYNC_ENDPOINT_REGISTRY['visits'], visits, Visit, 1),
]


@pytest.mark.parametrize("cls,module,model,item_id", CASES)
def test_list_and_get(dummy_client, context, paginator_factory, cls, module, model, item_id):
    """Test that list and get."""
    ep = cls(dummy_client, context)
    capture = paginator_factory(module, [{cls._id_param: item_id}])

    list_kwargs = {"study_key": "S1"} if getattr(ep, "requires_study_key", True) else {}
    result = list(ep.list(**list_kwargs))

    expected_path = "/api/v1/edc/studies"
    if getattr(ep, "requires_study_key", True):
        expected_path += f"/S1/{cls.PATH}"
    elif cls.PATH:
        expected_path += f"/{cls.PATH}"
    assert capture["path"] == expected_path
    assert isinstance(result[0], model)

    get_args = ("S1", item_id) if getattr(ep, "requires_study_key", True) else (None, item_id)
    got = ep.get(*get_args)
    assert isinstance(got, model)


@pytest.mark.asyncio
@pytest.mark.parametrize("cls,module,model,item_id", ASYNC_CASES)
async def test_async_list_and_get(
    dummy_client,
    context,
    async_paginator_factory,
    cls,
    module,
    model,
    item_id,
):
    """Test that async list and get asynchronously."""
    ep = cls(dummy_client, context)
    capture = async_paginator_factory(module, [{cls._id_param: item_id}])

    list_kwargs = {"study_key": "S1"} if getattr(ep, "requires_study_key", True) else {}
    result = [item async for item in ep.async_list(**list_kwargs)]

    expected_path = "/api/v1/edc/studies"
    if getattr(ep, "requires_study_key", True):
        expected_path += f"/S1/{cls.PATH}"
    elif cls.PATH:
        expected_path += f"/{cls.PATH}"
    assert capture["path"] == expected_path
    assert isinstance(result[0], model)

    get_args = ("S1", item_id) if getattr(ep, "requires_study_key", True) else (None, item_id)
    got = await ep.async_get(*get_args)
    assert isinstance(got, model)
