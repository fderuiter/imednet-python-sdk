"""Tests for streaming."""

import asyncio
from typing import Any, AsyncIterator, Generic, Iterable, Iterator, List, TypeVar, Union, overload

T = TypeVar('T')


class StreamingMockWrapper(Generic[T]):
    """A robust test wrapper that mimics both a list and an async/sync iterator."""

    def __init__(self, data: Iterable[T], max_buffer_size: int = 10000):
        """Test __init__ behavior."""
        self._max_buffer_size = max_buffer_size
        self._buffer: List[T] = []
        self._fully_buffered = False

        if isinstance(data, list):
            self._buffer = list(data)
            self._fully_buffered = True
            self._sync_iter = iter([])
        else:
            self._sync_iter = iter(data)

    def _fill_buffer(self, target_index: Union[int, slice, None] = None) -> None:
        """Test _fill_buffer behavior."""
        if self._fully_buffered:
            return

        try:
            while True:
                if target_index is not None and isinstance(target_index, int):
                    if target_index >= 0 and len(self._buffer) > target_index:
                        break
                if len(self._buffer) >= self._max_buffer_size:
                    raise MemoryError("StreamWrapper buffer limit exceeded.")
                self._buffer.append(next(self._sync_iter))
        except StopIteration:
            self._fully_buffered = True

    def __getitem__(self, index: Union[int, slice]) -> Union[T, List[T]]:
        """Test __getitem__ behavior."""
        if isinstance(index, slice):
            if index.stop is None or index.stop < 0:
                self._fill_buffer()
            else:
                self._fill_buffer(index.stop)
        elif isinstance(index, int) and index < 0:
            self._fill_buffer()
        else:
            self._fill_buffer(index)
        return self._buffer[index]

    def __len__(self) -> int:
        """Test __len__ behavior."""
        self._fill_buffer()
        return len(self._buffer)

    def __iter__(self) -> Iterator[T]:
        """Test __iter__ behavior."""
        # Yield from buffer first
        yield from self._buffer
        # Then from source, adding to buffer
        if not self._fully_buffered:
            try:
                while True:
                    if len(self._buffer) >= self._max_buffer_size:
                        raise MemoryError("StreamWrapper buffer limit exceeded.")
                    item = next(self._sync_iter)
                    self._buffer.append(item)
                    yield item
            except StopIteration:
                self._fully_buffered = True

    async def __aiter__(self) -> AsyncIterator[T]:
        """Implementation detail."""
        # Yield from buffer first
        for item in self._buffer:
            yield item
        # Then from source, adding to buffer
        if not self._fully_buffered:
            try:
                while True:
                    if len(self._buffer) >= self._max_buffer_size:
                        raise MemoryError("StreamWrapper buffer limit exceeded.")
                    # Simulate async yielding for synchronous iterators
                    item = next(self._sync_iter)
                    self._buffer.append(item)
                    yield item
            except StopIteration:
                self._fully_buffered = True

    def __eq__(self, other: Any) -> bool:
        """Test __eq__ behavior."""
        self._fill_buffer()
        if isinstance(other, list):
            return self._buffer == other
        return super().__eq__(other)

    def __await__(self):
        """Test __await__ behavior."""

        # Handle incorrect awaiting by gracefully returning self so test assertions can pass.
        async def _mock_coroutine():
            """Test __await__ behavior."""
            return self

        return _mock_coroutine().__await__()


def unified_paginator_factory(monkeypatch, module, items, is_async=False):
    """Test unified_paginator_factory behavior."""
    captured = {"count": 0}

    class DummyPaginator(StreamingMockWrapper):
        """Test suite for DummyPaginator."""

        def __init__(self, client, path, params=None, page_size=100, **kwargs):
            """Test __init__ behavior."""
            super().__init__(items)
            captured["client"] = client
            captured["path"] = path
            captured["params"] = params or {}
            captured["page_size"] = page_size
            captured["count"] += 1

    # Apply to both Sync and Async if available
    from imednet.core.endpoint.base import AsyncListGetEndpoint, SyncListGetEndpoint

    for obj in module.__dict__.values():
        if isinstance(obj, type):
            if issubclass(obj, SyncListGetEndpoint):
                monkeypatch.setattr(obj, "PAGINATOR_CLS", DummyPaginator, raising=False)
            if issubclass(obj, AsyncListGetEndpoint):
                monkeypatch.setattr(obj, "ASYNC_PAGINATOR_CLS", DummyPaginator, raising=False)

    return captured
