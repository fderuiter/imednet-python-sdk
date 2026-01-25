import pytest

import imednet.endpoints.subjects as subjects
from imednet.models.subjects import Subject


def test_list_builds_path_with_default(
    dummy_client, context, paginator_factory, patch_build_filter
):
    context.set_default_study_key("S1")
    ep = subjects.SubjectsEndpoint(dummy_client, context)
    capture = paginator_factory(subjects, [{"subjectKey": "x"}])
    patch = patch_build_filter(subjects)

    result = ep.list()

    assert capture["path"] == "/api/v1/edc/studies/S1/subjects"
    assert capture["params"] == {"filter": "FILTERED"}
    assert patch["filters"] == {"studyKey": "S1"}
    assert isinstance(result[0], Subject)


def test_get_not_found(monkeypatch, dummy_client, context, paginator_factory):
    ep = subjects.SubjectsEndpoint(dummy_client, context)
    paginator_factory(subjects, [])

    with pytest.raises(ValueError):
        ep.get("S1", "X")
