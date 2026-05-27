from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from pathlib import Path
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")

# Keep per-chunk memory bounded for large-study payloads while still
# amortizing DB/API overhead across each batch.
DEFAULT_CHUNK_SIZE = 5_000


def iter_chunks(items: Iterable[T], *, chunk_size: int = DEFAULT_CHUNK_SIZE) -> Iterator[list[T]]:
    """Yield ``items`` in bounded chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    chunk: list[T] = []
    for item in items:
        chunk.append(item)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


class ChunkedRecordPipeline:
    """Chunked iteration utilities for large-study workflows."""

    def __init__(self, *, chunk_size: int = DEFAULT_CHUNK_SIZE) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")
        self.chunk_size = chunk_size

    def map_chunks(self, items: Iterable[T], mapper: Callable[[T], R]) -> Iterator[list[R]]:
        """Apply ``mapper`` to ``items`` and yield mapped chunks."""
        for chunk in iter_chunks(items, chunk_size=self.chunk_size):
            mapped = [mapper(item) for item in chunk]
            yield mapped

    def write_parquet_chunks(
        self,
        rows: Iterable[dict[str, object]],
        *,
        output_dir: str | Path,
        filename_prefix: str = "records",
    ) -> list[Path]:
        """Write chunked parquet files and return written file paths."""
        import pandas as pd

        target_dir = Path(output_dir).expanduser()
        target_dir.mkdir(parents=True, exist_ok=True)

        written: list[Path] = []
        for index, chunk in enumerate(iter_chunks(rows, chunk_size=self.chunk_size), start=1):
            frame = pd.DataFrame(chunk)
            destination = target_dir / f"{filename_prefix}_chunk_{index:05d}.parquet"
            frame.to_parquet(destination, index=False)
            written.append(destination)
        return written
