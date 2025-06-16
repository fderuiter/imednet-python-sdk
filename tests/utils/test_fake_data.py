import imednet.testing.fake_data as fake_data
from imednet.models import Interval, Query, Record, Site, Subject


def test_fake_subject_parses() -> None:
    data = fake_data.fake_subject()
    obj = Subject.from_json(data)
    assert isinstance(obj, Subject)


def test_fake_site_parses() -> None:
    data = fake_data.fake_site()
    obj = Site.from_json(data)
    assert isinstance(obj, Site)


def test_fake_interval_parses() -> None:
    data = fake_data.fake_interval()
    obj = Interval.from_json(data)
    assert isinstance(obj, Interval)


def test_fake_query_parses() -> None:
    data = fake_data.fake_query()
    obj = Query.from_json(data)
    assert isinstance(obj, Query)


def test_fake_record_parses() -> None:
    data = fake_data.fake_record()
    obj = Record.from_json(data)
    assert isinstance(obj, Record)
