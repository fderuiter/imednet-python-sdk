"""Test Pagination Guarantees module."""

import itertools

import httpx
import pytest
import respx

from imednet.core.paginator import Paginator
from imednet.errors import PaginationError


@respx.mock
def test_empty_result_set_stops_immediately() -> None:
    """Test the test empty result set stops immediately functionality."""
    respx.get("https://api.test/items").mock(
        return_value=httpx.Response(200, json={"data": [], "pagination": {"totalPages": 0}})
    )
    with httpx.Client(base_url="https://api.test") as client:
        paginator = Paginator(client, "/items")
        assert list(paginator) == []
        assert paginator.cursor is None


@respx.mock
def test_single_page_iteration() -> None:
    """Test the test single page iteration functionality."""
    respx.get("https://api.test/items").mock(
        return_value=httpx.Response(200, json={"data": [1, 2], "pagination": {"totalPages": 1}})
    )
    with httpx.Client(base_url="https://api.test") as client:
        paginator = Paginator(client, "/items", page_size=50)
        assert paginator.page_size == 50
        assert paginator.cursor is None
        assert list(paginator) == [1, 2]
        assert paginator.cursor is None


@respx.mock
def test_last_page_partial_results() -> None:
    """Test the test last page partial results functionality."""
    calls: list[int] = []

    def responder(request: httpx.Request) -> httpx.Response:
        """Test the responder functionality."""
        page = int(request.url.params["page"])
        calls.append(page)
        if page == 0:
            return httpx.Response(200, json={"data": [1, 2], "pagination": {"totalPages": 2}})
        return httpx.Response(200, json={"data": [3], "pagination": {"totalPages": 2}})

    respx.get("https://api.test/items").mock(side_effect=responder)
    with httpx.Client(base_url="https://api.test") as client:
        paginator = Paginator(client, "/items", page_size=2)
        assert list(paginator) == [1, 2, 3]
        assert calls == [0, 1]


@respx.mock
def test_missing_cursor_raises_typed_error() -> None:
    """Test the test missing cursor raises typed error functionality."""
    respx.get("https://api.test/items").mock(
        return_value=httpx.Response(200, json={"data": [1, 2], "pagination": {}})
    )
    with httpx.Client(base_url="https://api.test") as client:
        paginator = Paginator(client, "/items", page_size=2)
        with pytest.raises(PaginationError, match="missing required 'totalPages'"):
            list(paginator)


@respx.mock
def test_malformed_cursor_raises_typed_error() -> None:
    """Test the test malformed cursor raises typed error functionality."""
    respx.get("https://api.test/items").mock(
        return_value=httpx.Response(
            200, json={"data": [1], "pagination": {"totalPages": "not-an-integer"}}
        )
    )
    with httpx.Client(base_url="https://api.test") as client:
        paginator = Paginator(client, "/items")
        with pytest.raises(PaginationError, match="must be an integer"):
            list(paginator)


@respx.mock
def test_large_result_set_iteration_is_lazy_and_bounded() -> None:
    """Test the test large result set iteration is lazy and bounded functionality."""
    calls: list[int] = []
    total_pages = 100_000

    def responder(request: httpx.Request) -> httpx.Response:
        """Test the responder functionality."""
        page = int(request.url.params["page"])
        calls.append(page)
        return httpx.Response(
            200,
            json={"data": [page], "pagination": {"totalPages": total_pages}},
        )

    respx.get("https://api.test/items").mock(side_effect=responder)
    with httpx.Client(base_url="https://api.test") as client:
        paginator = Paginator(client, "/items", page_size=1)
        first_three = list(itertools.islice(paginator, 3))
        assert first_three == [0, 1, 2]
        assert calls == [0, 1, 2]


@respx.mock
def test_iteration_can_be_interrupted_and_resumed() -> None:
    """Test the test iteration can be interrupted and resumed functionality."""
    calls: list[int] = []

    def responder(request: httpx.Request) -> httpx.Response:
        """Test the responder functionality."""
        page = int(request.url.params["page"])
        calls.append(page)
        if page == 0:
            return httpx.Response(200, json={"data": [1, 2], "pagination": {"totalPages": 2}})
        return httpx.Response(200, json={"data": [3], "pagination": {"totalPages": 2}})

    respx.get("https://api.test/items").mock(side_effect=responder)
    with httpx.Client(base_url="https://api.test") as client:
        paginator = Paginator(client, "/items", page_size=2)
        iterator = iter(paginator)
        assert next(iterator) == 1
        assert list(iterator) == [2, 3]
        assert calls == [0, 1]
