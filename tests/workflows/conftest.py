import types

import pytest

from imednet.testing import fake_data
from imednet.validation.cache import SchemaCache


@pytest.fixture
def schema() -> SchemaCache:
    forms = fake_data.fake_forms_for_cache(1, study_key="S")
    variables = fake_data.fake_variables_for_cache(forms, vars_per_form=1, study_key="S")
    forms_ep = types.SimpleNamespace(list=lambda **_: forms)

    def list_vars(*_, form_id=None, **__):
        return [v for v in variables if form_id is None or v.form_id == form_id]

    vars_ep = types.SimpleNamespace(list=list_vars)

    cache = SchemaCache()
    from typing import Any, cast

    cache.refresh(cast(Any, forms_ep), cast(Any, vars_ep), study_key="S")
    return cache
