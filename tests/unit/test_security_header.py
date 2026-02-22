import pytest

from imednet.utils.security import validate_header_value


def test_validate_header_value_success():
    """Verify that valid header values pass validation."""
    validate_header_value("Test-Header", "valid_value")
    validate_header_value("Test-Header", "valid value with spaces")


def test_validate_header_value_newline_injection():
    """Verify that values with newlines raise ValueError."""
    with pytest.raises(ValueError, match="Test-Header must not contain newlines"):
        validate_header_value("Test-Header", "value\nnewline")


def test_validate_header_value_carriage_return_injection():
    """Verify that values with carriage returns raise ValueError."""
    with pytest.raises(ValueError, match="Test-Header must not contain newlines"):
        validate_header_value("Test-Header", "value\rreturn")
