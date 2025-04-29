from datetime import datetime

from imednet.models.queries import Query, QueryComment


def test_query_comment_creation():
    # Test basic creation
    comment = QueryComment(
        sequence=1,
        annotationStatus="OPEN",
        user="test_user",
        comment="test comment",
        closed=False,
        date=datetime.now(),
    )
    assert comment.sequence == 1
    assert comment.annotation_status == "OPEN"
    assert comment.user == "test_user"
    assert comment.comment == "test comment"
    assert comment.closed is False
    assert isinstance(comment.date, datetime)


def test_query_comment_from_json():
    json_data = {
        "sequence": 1,
        "annotationStatus": "OPEN",
        "user": "test_user",
        "comment": "test comment",
        "closed": False,
        "date": "2023-01-01T00:00:00",
    }
    comment = QueryComment.from_json(json_data)
    assert comment.sequence == 1
    assert comment.annotation_status == "OPEN"


def test_query_creation():
    # Test basic creation
    query = Query(
        studyKey="STUDY1",
        subjectId=123,
        subjectOid="S_123",
        annotationType="QUERY",
        annotationId=456,
        description="test query",
        recordId=789,
        variable="VAR1",
        subjectKey="KEY1",
    )
    assert query.study_key == "STUDY1"
    assert query.subject_id == 123
    assert query.annotation_type == "QUERY"


def test_query_with_comments():
    query_data = {
        "studyKey": "STUDY1",
        "subjectId": 123,
        "queryComments": [
            {
                "sequence": 1,
                "annotationStatus": "OPEN",
                "user": "user1",
                "comment": "comment1",
                "closed": False,
                "date": "2023-01-01T00:00:00",
            }
        ],
    }
    query = Query.from_json(query_data)
    assert len(query.query_comments) == 1
    assert query.query_comments[0].user == "user1"


def test_default_values():
    query = Query()
    assert query.study_key == ""
    assert query.subject_id == 0
    assert len(query.query_comments) == 0


def test_field_validators():
    # Test integer parsing
    comment = QueryComment(sequence="1")
    assert comment.sequence == 1

    # Test boolean parsing
    comment = QueryComment(closed="true")
    assert comment.closed is True

    # Test datetime parsing
    comment = QueryComment(date="2023-01-01T00:00:00")
    assert isinstance(comment.date, datetime)
