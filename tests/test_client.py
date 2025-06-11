import pytest
import requests_mock

from imednet_py.client import ImednetAPIError, ImednetClient
from imednet_py.models import Record, Site, Study


def test_session_headers() -> None:
    client = ImednetClient(api_key="key", security_key="sec")
    assert client.session.headers["x-api-key"] == "key"
    assert client.session.headers["x-imn-security-key"] == "sec"
    assert client.base_url == "https://edc.prod.imednetapi.com/api/v1/edc/"


def test_env_var_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IMEDNET_API_KEY", "env_key")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "env_sec")
    client = ImednetClient()
    assert client.session.headers["x-api-key"] == "env_key"
    assert client.session.headers["x-imn-security-key"] == "env_sec"


def test_missing_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("IMEDNET_API_KEY", raising=False)
    monkeypatch.delenv("IMEDNET_SECURITY_KEY", raising=False)
    with pytest.raises(ValueError):
        ImednetClient()


def test_request_success() -> None:
    client = ImednetClient(api_key="key", security_key="sec")
    with requests_mock.Mocker() as m:
        m.get(
            "https://edc.prod.imednetapi.com/api/v1/edc/hello",
            json={"hello": "world"},
            headers={"Content-Type": "application/json"},
        )
        result = client._request("GET", "hello")
        assert result == {"hello": "world"}


def test_request_error() -> None:
    client = ImednetClient(api_key="key", security_key="sec")
    with requests_mock.Mocker() as m:
        m.get(
            "https://edc.prod.imednetapi.com/api/v1/edc/missing",
            status_code=404,
            json={"metadata": {"error": {"code": "NOT_FOUND", "description": "Nope"}}},
            headers={"Content-Type": "application/json"},
        )
        with pytest.raises(ImednetAPIError) as exc:
            client._request("GET", "missing")
        assert exc.value.code == "NOT_FOUND"
        assert exc.value.description == "Nope"


def test_get_studies_wrapper() -> None:
    client = ImednetClient(api_key="key", security_key="sec")
    with requests_mock.Mocker() as m:
        m.get(
            "https://edc.prod.imednetapi.com/api/v1/edc/studies",
            json={"data": [{"key": "S1"}]},
            headers={"Content-Type": "application/json"},
        )
        result = client.get_studies(page=2, size=5)
        req = m.request_history[0]
        assert req.qs == {"page": ["2"], "size": ["5"]}
        assert isinstance(result[0], Study)


def test_get_sites_wrapper() -> None:
    client = ImednetClient(api_key="key", security_key="sec")
    with requests_mock.Mocker() as m:
        m.get(
            "https://edc.prod.imednetapi.com/api/v1/edc/studies/ABC/sites",
            json={"data": [{"key": "site1"}]},
            headers={"Content-Type": "application/json"},
        )
        sites = client.get_sites("ABC", filter="active")
        req = m.request_history[0]
        assert req.qs == {"filter": ["active"]}
        assert isinstance(sites[0], Site)


def test_get_records_wrapper() -> None:
    client = ImednetClient(api_key="key", security_key="sec")
    with requests_mock.Mocker() as m:
        m.get(
            "https://edc.prod.imednetapi.com/api/v1/edc/studies/XYZ/records",
            json={"data": [{"key": "rec1"}]},
            headers={"Content-Type": "application/json"},
        )
        recs = client.get_records("XYZ", recordDataFilter="latest")
        req = m.request_history[0]
        assert req.qs.get("recorddatafilter") == ["latest"]
        assert isinstance(recs[0], Record)


def test_iter_records_pagination() -> None:
    client = ImednetClient(api_key="key", security_key="sec")
    pages = [
        {
            "data": [{"key": "r1"}, {"key": "r2"}],
            "metadata": {"pagination": {"currentPage": 0, "totalPages": 3}},
        },
        {
            "data": [{"key": "r3"}],
            "metadata": {"pagination": {"currentPage": 1, "totalPages": 3}},
        },
        {
            "data": [{"key": "r4"}],
            "metadata": {"pagination": {"currentPage": 2, "totalPages": 3}},
        },
    ]

    with requests_mock.Mocker() as m:
        m.get(
            "https://edc.prod.imednetapi.com/api/v1/edc/studies/ABC/records",
            [
                {"json": pages[0], "headers": {"Content-Type": "application/json"}},
                {"json": pages[1], "headers": {"Content-Type": "application/json"}},
                {"json": pages[2], "headers": {"Content-Type": "application/json"}},
            ],
        )

        records = client.get_all_records("ABC", page_size=2)

        assert [r.key for r in records] == ["r1", "r2", "r3", "r4"]
        assert len(m.request_history) == 3
