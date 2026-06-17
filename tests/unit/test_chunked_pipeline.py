from __future__ import annotations

import pytest

from imednet_workflows.chunked_pipeline import ChunkedRecordPipeline, iter_chunks


def test_iter_chunks_splits_batches() -> None:
    chunks = list(iter_chunks(range(5), chunk_size=2))
    assert chunks == [[0, 1], [2, 3], [4]]


def test_iter_chunks_rejects_invalid_chunk_size() -> None:
    with pytest.raises(ValueError, match="chunk_size must be greater than zero"):
        list(iter_chunks([1, 2], chunk_size=0))


def test_chunked_record_pipeline_maps_in_chunks() -> None:
    pipeline = ChunkedRecordPipeline(chunk_size=2)
    mapped = list(pipeline.map_chunks([1, 2, 3], lambda value: value * 10))
    assert mapped == [[10, 20], [30]]

def test_write_parquet_chunks_writes_files(tmp_path) -> None:
    pipeline = ChunkedRecordPipeline(chunk_size=2)
    rows = [{"a": 1}, {"a": 2}, {"a": 3}]
    written = pipeline.write_parquet_chunks(rows, output_dir=tmp_path)
    assert len(written) == 2
    assert written[0].name == "records_chunk_00001.parquet"
    assert written[1].name == "records_chunk_00002.parquet"
    assert written[0].exists()
    assert written[1].exists()
    
    import pandas as pd
    df1 = pd.read_parquet(written[0])
    assert len(df1) == 2
    assert df1["a"].tolist() == [1, 2]
    
    df2 = pd.read_parquet(written[1])
    assert len(df2) == 1
    assert df2["a"].tolist() == [3]

def test_pipeline_rejects_invalid_chunk_size() -> None:
    with pytest.raises(ValueError, match="chunk_size must be greater than zero"):
        ChunkedRecordPipeline(chunk_size=0)
