from __future__ import annotations

import json
from datetime import datetime
from types import SimpleNamespace

from imednet.workflows.incremental_sync import IncrementalSyncWorkflow


def make_revision(record_id: int, date: str):
    return SimpleNamespace(record_id=record_id, date_created=datetime.fromisoformat(date))


def make_record(record_id: int):
    return SimpleNamespace(record_id=record_id)


def test_sync_without_state(tmp_path):
    state_file = tmp_path / "state.json"

    sdk = SimpleNamespace()
    revisions = [make_revision(1, "2024-01-01T00:00:00"), make_revision(2, "2024-01-02T00:00:00")]
    sdk.record_revisions = SimpleNamespace(list=lambda study_key, filter=None: revisions)
    sdk.records = SimpleNamespace(get=lambda study_key, rid: make_record(rid))

    wf = IncrementalSyncWorkflow(sdk, str(state_file))
    records = wf.sync("STUDY")

    assert len(records) == 2
    assert json.load(open(state_file, "r"))["last_sync"] == "2024-01-02T00:00:00"


def test_sync_with_state(tmp_path):
    state_file = tmp_path / "state.json"
    json.dump({"last_sync": "2024-01-01T00:00:00"}, open(state_file, "w"))

    captured_filter = {}

    def list_mock(study_key, filter=None):
        captured_filter["value"] = filter
        return [make_revision(5, "2024-01-03T00:00:00")]

    sdk = SimpleNamespace()
    sdk.record_revisions = SimpleNamespace(list=list_mock)
    sdk.records = SimpleNamespace(get=lambda study_key, rid: make_record(rid))

    wf = IncrementalSyncWorkflow(sdk, str(state_file))
    wf.sync("STUDY")

    assert captured_filter["value"] == "dateCreated>2024-01-01T00:00:00"
    assert json.load(open(state_file, "r"))["last_sync"] == "2024-01-03T00:00:00"
