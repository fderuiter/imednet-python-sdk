"""Security tests for RecordsEndpoint."""

import pytest

from imednet.endpoints.records import RecordsEndpoint


def test_create_email_notify_header_injection(dummy_client, context):
    """Test that header injection via email_notify raises ValueError."""
    ep = RecordsEndpoint(dummy_client, context)

    # Test with newline
    with pytest.raises(ValueError, match="email_notify must not contain newlines"):
        ep.create("S1", [{"foo": "bar"}], email_notify="test@example.com\nBcc: evil@example.com")

    # Test with carriage return
    with pytest.raises(ValueError, match="email_notify must not contain newlines"):
        ep.create("S1", [{"foo": "bar"}], email_notify="test@example.com\rBcc: evil@example.com")
