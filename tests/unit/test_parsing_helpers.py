from __future__ import annotations

import json
from pathlib import Path

from imednet.models.records import Record
from imednet.models.sites import Site
from imednet.models.studies import Study
from imednet.utils.parsing import parse_records, parse_sites, parse_studies

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def load(name: str) -> dict:
    with open(FIXTURES / name, "r", encoding="utf-8") as fh:
        return json.load(fh)


def test_parse_studies() -> None:
    data = load("sample_studies.json")
    studies = parse_studies(data)
    assert isinstance(studies, list)
    assert isinstance(studies[0], Study)
    assert studies[0].study_key == "S1"


def test_parse_sites() -> None:
    data = load("sample_sites.json")
    sites = parse_sites(data)
    assert isinstance(sites, list)
    assert isinstance(sites[0], Site)
    assert sites[0].site_id == 1


def test_parse_records() -> None:
    data = load("sample_records.json")
    records = parse_records(data)
    assert isinstance(records, list)
    assert isinstance(records[0], Record)
    assert records[0].record_id == 100
    assert records[0].record_data == {"v1": "a"}
