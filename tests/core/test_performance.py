import fcntl
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict

import pyarrow as pa
import pytest
from pydantic import BaseModel

from imednet.models.records import Record
from imednet.testing.fake_data import fake_record
from imednet.validation.cache import SchemaCache

try:
    from imednet_sinks.warehouse import _records_to_arrow_table
except ImportError:
    def _records_to_arrow_table(records):
        rows = [
            {
                "record_id": getattr(r, "record_id", None),
                "form_id": getattr(r, "form_id", None),
                "visit_id": getattr(r, "visit_id", None),
                "subject_key": getattr(r, "subject_key", None),
                **dict(getattr(r, "record_data", {}) or {}),
            }
            for r in records
        ]
        return pa.Table.from_pylist(rows)

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.performance

def generate_records(count: int, cache: SchemaCache) -> list:
    records = []
    for _ in range(count):
        data = fake_record(cache)
        records.append(Record.model_validate(data))
    return records

def run_benchmarks(record_count: int = 10000) -> Dict[str, float]:
    results = {}
    cache = SchemaCache()

    start = time.time()
    records = generate_records(record_count, cache)
    elapsed = time.time() - start
    results["record_generation_latency"] = elapsed
    print(f"Generated {record_count} records in {elapsed:.4f}s")

    start = time.time()
    for r in records:
        if isinstance(r, BaseModel):
            r.model_dump(by_alias=True)
        else:
            r.model_dump()
    elapsed = time.time() - start
    results["mongo_conversion_latency"] = elapsed
    print(f"Mongo conversion (serialization) for {record_count} records in {elapsed:.4f}s")

    start = time.time()
    table = _records_to_arrow_table(records)
    elapsed = time.time() - start
    results["snowflake_arrow_conversion_latency"] = elapsed
    print(f"Snowflake Arrow conversion for {record_count} records in {elapsed:.4f}s")

    start = time.time()
    nodes = []
    edges = []
    for r in records:
        nodes.append({"id": r.record_id, "label": "Record"})
        if getattr(r, "subject_key", None):
            edges.append({"from": r.subject_key, "to": r.record_id, "type": "HAS_RECORD"})
    elapsed = time.time() - start
    results["neo4j_conversion_latency"] = elapsed
    print(f"Neo4j Graph conversion for {record_count} records in {elapsed:.4f}s")

    return results

def test_performance_suite():
    historical_file = Path("performance_cache.json")
    threshold = 0.05

    print("Running SDK Observability & Performance Suite...")
    current_results = run_benchmarks(10000)

    # Ensure file exists before trying to open for a+ (which doesn't exist in standard open modes safely without truncating, so we use 'a+' or just touch it)
    if not historical_file.exists():
        historical_file.touch()

    degradations = []
    
    with open(historical_file, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        
        try:
            f.seek(0)
            content = f.read()
            if content:
                history = json.loads(content)
            else:
                history = {}
        except Exception:
            history = {}

        for metric, current_val in current_results.items():
            if metric in history:
                historical_val = history[metric]
                diff = (current_val - historical_val) / historical_val
                if diff > threshold:
                    degradations.append(
                        f"{metric}: {current_val:.4f}s exceeds baseline {historical_val:.4f}s by {diff * 100:.1f}% (> 5%)"
                    )
                else:
                    print(f"{metric} OK: {current_val:.4f}s (baseline: {historical_val:.4f}s, diff: {diff * 100:.1f}%)")
            else:
                print(f"{metric} recorded as new baseline: {current_val:.4f}s")
                history[metric] = current_val

        f.seek(0)
        f.truncate()
        json.dump(history, f, indent=2)
        
        fcntl.flock(f, fcntl.LOCK_UN)

    assert not degradations, "Performance Regressions Detected:\n" + "\n".join(degradations)
