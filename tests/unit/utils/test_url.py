import pytest

from imednet.utils.url import sanitize_base_url


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://x/api", "https://x"),
        ("https://x/api/", "https://x"),
        ("https://x//", "https://x"),
        ("https://x", "https://x"),
        ("https://x/api ", "https://x"),
        (" https://x/api", "https://x"),
        (" https://x/api ", "https://x"),
    ],
)
def test_sanitize_base_url(url: str, expected: str) -> None:
    assert sanitize_base_url(url) == expected
