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


def test_redact_url_query() -> None:
    """Test URL query parameter redaction."""
    url = "https://api.example.com/v1/resource?api_key=secret123&token=abc&other=value"
    expected = "https://api.example.com/v1/resource?api_key=***&token=***&other=value"
    assert redact_url_query(url) == expected

    # Test custom sensitive params
    url = "https://example.com?user=me&pass=1234"
    expected = "https://example.com?user=me&pass=***"
    assert redact_url_query(url, sensitive_params={"pass"}) == expected

    # Test no sensitive params
    url = "https://example.com?q=search"
    assert redact_url_query(url) == url

    # Test empty params
    assert redact_url_query("https://example.com") == "https://example.com"
