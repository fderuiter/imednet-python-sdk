from imednet_py.client import ImednetClient


def test_session_headers() -> None:
    client = ImednetClient(api_key="key", security_key="sec")
    assert client.session.headers["x-api-key"] == "key"
    assert client.session.headers["x-imn-security-key"] == "sec"
