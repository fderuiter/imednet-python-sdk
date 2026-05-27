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
