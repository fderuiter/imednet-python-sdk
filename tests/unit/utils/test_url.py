import pytest

from imednet.utils.url import redact_url_query, sanitize_base_url


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://x/api", "https://x"),
        ("https://x/api/", "https://x"),
        ("https://x//", "https://x"),
        ("https://x", "https://x"),
    ],
)
def test_sanitize_base_url(url: str, expected: str) -> None:
    assert sanitize_base_url(url) == expected


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://api.com/v1/users", "https://api.com/v1/users"),
        ("https://api.com/v1/users?token=secret", "https://api.com/v1/users?REDACTED"),
        ("https://api.com/v1/users?a=1&b=2", "https://api.com/v1/users?REDACTED"),
        ("https://api.com/v1/users#fragment", "https://api.com/v1/users#fragment"),
        ("https://api.com/v1/users?query=1#frag", "https://api.com/v1/users?REDACTED#frag"),
    ],
)
def test_redact_url_query(url: str, expected: str) -> None:
    assert redact_url_query(url) == expected
