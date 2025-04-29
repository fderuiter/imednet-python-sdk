from datetime import datetime

from imednet.models.visits import Visit


def test_visit_default_values():
    visit = Visit()
    assert visit.visit_id == 0
    assert visit.study_key == ""
    assert visit.interval_id == 0
    assert visit.interval_name == ""
    assert visit.subject_id == 0
    assert visit.subject_key == ""
    assert visit.start_date is None
    assert visit.end_date is None
    assert visit.due_date is None
    assert visit.visit_date is None
    assert visit.visit_date_form == ""
    assert visit.visit_date_question == ""
    assert visit.deleted is False


def test_visit_from_json():
    test_data = {
        "visitId": 123,
        "studyKey": "STUDY01",
        "intervalId": 456,
        "intervalName": "Week 1",
        "subjectId": 789,
        "subjectKey": "SUBJ01",
        "startDate": "2023-01-01T00:00:00",
        "endDate": "2023-01-02T00:00:00",
        "dueDate": "2023-01-03T00:00:00",
        "visitDate": "2023-01-04T00:00:00",
        "visitDateForm": "FORM01",
        "visitDateQuestion": "Q1",
        "deleted": "true",
        "dateCreated": "2023-01-05T00:00:00",
        "dateModified": "2023-01-06T00:00:00",
    }

    visit = Visit.from_json(test_data)

    assert visit.visit_id == 123
    assert visit.study_key == "STUDY01"
    assert visit.interval_id == 456
    assert visit.interval_name == "Week 1"
    assert visit.subject_id == 789
    assert visit.subject_key == "SUBJ01"
    assert visit.start_date == datetime(2023, 1, 1)
    assert visit.end_date == datetime(2023, 1, 2)
    assert visit.due_date == datetime(2023, 1, 3)
    assert visit.visit_date == datetime(2023, 1, 4)
    assert visit.visit_date_form == "FORM01"
    assert visit.visit_date_question == "Q1"
    assert visit.deleted is True
    assert visit.date_created == datetime(2023, 1, 5)
    assert visit.date_modified == datetime(2023, 1, 6)


def test_visit_empty_dates():
    test_data = {"visitId": 1, "startDate": "", "endDate": None, "dueDate": "", "visitDate": None}

    visit = Visit.from_json(test_data)

    assert visit.start_date is None
    assert visit.end_date is None
    assert visit.due_date is None
    assert visit.visit_date is None


def test_visit_invalid_types():
    test_data = {"visitId": "invalid", "intervalId": None, "subjectId": "", "deleted": "not_a_bool"}

    visit = Visit.from_json(test_data)

    assert visit.visit_id == 0
    assert visit.interval_id == 0
    assert visit.subject_id == 0
    assert visit.deleted is False
