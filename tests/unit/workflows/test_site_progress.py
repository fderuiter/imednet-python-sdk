import datetime
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from imednet.models.queries import Query, QueryComment
from imednet.models.sites import Site
from imednet.models.subjects import Subject
from imednet.models.visits import Visit
from imednet.workflows.site_progress import SiteProgressWorkflow


def test_get_site_progress():
    # Prepare mock SDK with endpoint mocks
    sdk = MagicMock()
    sdk.sites.list.return_value = [
        Site(site_id=1, site_name="Site A"),
        Site(site_id=2, site_name="Site B"),
        Site(site_id=3, site_name="Site C"),
    ]

    subjects_map = {
        1: [Subject(subject_key="S1", site_id=1), Subject(subject_key="S2", site_id=1)],
        2: [Subject(subject_key="S3", site_id=2)],
        3: [],
    }

    def subjects_list(study_key, **filters):
        return subjects_map.get(filters.get("site_id"), [])

    sdk.subjects.list.side_effect = subjects_list

    visits_map = {
        "S1": [
            Visit(visit_id=1, subject_key="S1", visit_date=datetime.datetime.now()),
            Visit(visit_id=2, subject_key="S1", visit_date=None),
        ],
        "S2": [Visit(visit_id=3, subject_key="S2", visit_date=datetime.datetime.now())],
        "S3": [],
    }

    def visits_list(study_key, **filters):
        return visits_map.get(filters.get("subject_key"), [])

    sdk.visits.list.side_effect = visits_list

    qc_open = QueryComment(sequence=1, closed=False)
    qc_closed = QueryComment(sequence=1, closed=True)
    queries_map = {
        "S1": [Query(query_comments=[qc_open]), Query(query_comments=[qc_closed])],
        "S2": [],
        "S3": [Query(query_comments=[qc_open])],
    }

    def queries_list(study_key, **filters):
        return queries_map.get(filters.get("subject_key"), [])

    sdk.queries.list.side_effect = queries_list

    workflow = SiteProgressWorkflow(sdk)
    result = workflow.get_site_progress("STU")

    assert len(result) == 3

    sp1 = result[0]
    assert sp1.site_id == 1
    assert sp1.subjects_enrolled == 2
    assert sp1.visits_completed == 2
    assert sp1.open_queries == 1

    sp2 = result[1]
    assert sp2.site_id == 2
    assert sp2.subjects_enrolled == 1
    assert sp2.visits_completed == 0
    assert sp2.open_queries == 1

    sp3 = result[2]
    assert sp3.site_id == 3
    assert sp3.subjects_enrolled == 0
    assert sp3.visits_completed == 0
    assert sp3.open_queries == 0
