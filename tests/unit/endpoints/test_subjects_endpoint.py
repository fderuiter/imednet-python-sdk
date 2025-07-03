import imednet.endpoints.subjects as subjects
import pytest
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
    assert capture["params"] == {}
    assert patch == {}
    assert isinstance(result[0], Subject)


def test_get_not_found(monkeypatch, dummy_client, context):
    ep = subjects.SubjectsEndpoint(dummy_client, context)

    def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        return []

    monkeypatch.setattr(subjects.SubjectsEndpoint, "_list_impl", fake_impl)

    with pytest.raises(ValueError):
        ep.get("S1", "X")
