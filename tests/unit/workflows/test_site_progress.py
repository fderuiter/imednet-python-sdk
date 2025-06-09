from unittest.mock import MagicMock

from imednet.models.queries import Query, QueryComment
from imednet.models.sites import Site
from imednet.models.subjects import Subject
from imednet.models.visits import Visit
from imednet.workflows.site_progress import SiteProgressWorkflow


def test_get_site_progress_aggregates_counts():
    sdk = MagicMock()

    site1 = Site.model_validate({"siteId": 1, "siteName": "A"})
    site2 = Site.model_validate({"siteId": 2, "siteName": "B"})
    sdk.sites.list.return_value = [site1, site2]

    sub1 = Subject.model_validate({"subjectKey": "SUBJ1", "siteId": 1})
    sub2 = Subject.model_validate({"subjectKey": "SUBJ2", "siteId": 1})

    def subjects_list(study_key: str, *, site_id: int):
        return [sub1, sub2] if site_id == 1 else []

    sdk.subjects.list.side_effect = subjects_list

    visit1 = Visit.model_validate(
        {"visitId": 1, "subjectKey": "SUBJ1", "visitDate": "2020-01-01T00:00:00Z"}
    )
    visit2 = Visit.model_validate({"visitId": 2, "subjectKey": "SUBJ1"})
    visit3 = Visit.model_validate(
        {"visitId": 3, "subjectKey": "SUBJ2", "visitDate": "2020-01-02T00:00:00Z"}
    )

    def visits_list(study_key: str, *, subject_key):
        if set(subject_key) == {"SUBJ1", "SUBJ2"}:
            return [visit1, visit2, visit3]
        return []

    sdk.visits.list.side_effect = visits_list

    query1 = Query.model_validate(
        {
            "annotationId": 1,
            "subjectKey": "SUBJ1",
            "queryComments": [QueryComment.model_validate({"sequence": 1, "closed": False})],
        }
    )
    query2 = Query.model_validate(
        {
            "annotationId": 2,
            "subjectKey": "SUBJ2",
            "queryComments": [QueryComment.model_validate({"sequence": 1, "closed": True})],
        }
    )

    def queries_list(study_key: str, *, subject_key):
        if set(subject_key) == {"SUBJ1", "SUBJ2"}:
            return [query1, query2]
        return []

    sdk.queries.list.side_effect = queries_list

    wf = SiteProgressWorkflow(sdk)
    progress = wf.get_site_progress("STUDY")

    assert len(progress) == 2

    first = progress[0]
    assert first.site_id == 1
    assert first.subjects_enrolled == 2
    assert first.visits_completed == 2
    assert first.open_queries == 1

    second = progress[1]
    assert second.site_id == 2
    assert second.subjects_enrolled == 0
    assert second.visits_completed == 0
    assert second.open_queries == 0

    assert sdk.visits.list.call_count == 1
    assert sdk.queries.list.call_count == 1
