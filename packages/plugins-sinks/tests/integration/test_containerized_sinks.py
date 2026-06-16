import logging
import os
from typing import List

import pytest
from imednet_sinks import (
    MongoDbExportSink,
    Neo4jExportSink,
    Neo4jSinkConfig,
    export_to_mongodb,
    export_to_neo4j,
)

pytestmark = pytest.mark.skipif(
    os.getenv("IMEDNET_TEST_CONTAINERS") != "1", reason="Requires IMEDNET_TEST_CONTAINERS=1"
)


class DriftError(Exception):
    pass


class DriftFailingHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.WARNING and "Drift detected" in record.getMessage():
            raise DriftError(record.getMessage())


@pytest.fixture(autouse=True)
def fail_on_drift():
    logger = logging.getLogger("imednet.drift")
    handler = DriftFailingHandler()
    logger.addHandler(handler)
    yield
    logger.removeHandler(handler)


from dataclasses import dataclass


@dataclass
class FakeRecord:
    record_id: int
    subject_id: str
    subject_key: str
    form_id: int
    form_key: str
    visit_name: str
    visit_id: int
    record_data: dict


@pytest.fixture
def fake_records() -> List[FakeRecord]:
    return [
        FakeRecord(
            record_id=1,
            subject_id="SUBJ-001",
            subject_key="SUBJ-001",
            form_id=20,
            form_key="CLINICAL",
            visit_name="Screening",
            visit_id=10,
            record_data={"heart_rate": 80, "bp": "120/80"},
        ),
        FakeRecord(
            record_id=2,
            subject_id="SUBJ-002",
            subject_key="SUBJ-002",
            form_id=20,
            form_key="CLINICAL",
            visit_name="Screening",
            visit_id=10,
            record_data={"heart_rate": 75, "bp": "110/70"},
        ),
    ]


@pytest.fixture
def mock_record_mapper(monkeypatch, fake_records):
    from unittest.mock import MagicMock

    from imednet.integrations import export as export_mod

    class FakeMapper:
        def __init__(self, *args, **kwargs):
            pass

        def __iter__(self):
            return iter(fake_records)

    monkeypatch.setattr(export_mod, "_record_mapper", lambda *a, **kw: FakeMapper)


def test_mongodb_containerized_upserts(fake_records, monkeypatch):
    import pymongo

    uri = "mongodb://root:password@localhost:27017"
    database = "imednet_test"
    collection = "clinical_records"

    # Export records
    with MongoDbExportSink(uri, database, collection, "STUDY1") as sink:
        sink.write(fake_records)

    # Verify directly via PyMongo
    client = pymongo.MongoClient(uri)
    db = client[database]
    coll = db[collection]

    count = coll.count_documents({})
    assert count == 2

    doc1 = coll.find_one({"subject_id": "SUBJ-001"})
    assert doc1 is not None
    assert doc1["_id"] == "STUDY1/1"
    assert doc1["study_key"] == "STUDY1"
    assert doc1["form_key"] == "CLINICAL"
    assert doc1["record_data"]["heart_rate"] == 80


def test_neo4j_containerized_merges(fake_records, monkeypatch):
    import neo4j

    uri = "bolt://localhost:7687"
    auth = ("neo4j", "password")

    config = Neo4jSinkConfig(batch_size=10, idempotent=True)

    with Neo4jExportSink(uri, auth, "STUDY1", config=config) as sink:
        sink.write(fake_records)

    # Verify directly via Neo4j Driver
    driver = neo4j.GraphDatabase.driver(uri, auth=auth)
    with driver.session() as session:
        result = session.run("MATCH (n:Record) RETURN count(n) AS count")
        count = result.single()["count"]
        assert count == 2

        result2 = session.run("MATCH (n:Record {record_id: 2}) RETURN n.record_data AS record_data")
        import json

        record_data = json.loads(result2.single()["record_data"])
        assert record_data["heart_rate"] == 75

        # Verify topology mapping
        topology_query = (
            "MATCH path=(s:Study {study_key: 'STUDY1'})"
            "-[:HAS_SUBJECT]->(su:Subject {subject_key: 'SUBJ-001'})"
            "-[:HAS_VISIT]->(v:Visit {visit_id: 10})"
            "-[:HAS_RECORD]->(r:Record {record_id: 1}) "
            "RETURN count(path) AS paths"
        )
        result3 = session.run(topology_query)
        paths = result3.single()["paths"]
        assert paths == 1

    driver.close()
