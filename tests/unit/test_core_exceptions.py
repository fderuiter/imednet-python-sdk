"""Test Core Exceptions module."""

from imednet import errors


def test_api_error_str_includes_details() -> None:
    """Test the test api error str includes details functionality."""
    err = errors.ApiError({"msg": "bad"}, status_code=400)
    text = str(err)
    assert "Status Code: 400" in text
    assert "msg" in text


def test_exception_hierarchy() -> None:
    """Test the test exception hierarchy functionality."""
    assert issubclass(errors.AuthenticationError, errors.ApiError)
    assert issubclass(errors.AuthorizationError, errors.ApiError)
    assert issubclass(errors.NotFoundError, errors.ApiError)
    assert issubclass(errors.RateLimitError, errors.ApiError)
    assert issubclass(errors.ServerError, errors.ApiError)
    assert issubclass(errors.ValidationError, errors.ApiError)

    # New check
    assert issubclass(errors.ClientError, errors.ImednetError)
    assert issubclass(errors.PathTraversalValidationError, errors.ClientError)
    assert issubclass(errors.OrchestratorError, errors.ImednetError)
    assert issubclass(errors.FilterConflictError, errors.OrchestratorError)


def test_filter_conflict_error_keeps_conflicting_filters() -> None:
    """Test the test filter conflict error keeps conflicting filters functionality."""
    whitelist = {"STUDY-A"}
    blacklist = {"STUDY-B"}

    err = errors.FilterConflictError(whitelist=whitelist, blacklist=blacklist)

    assert err.whitelist == whitelist
    assert err.blacklist == blacklist
    assert "mutually exclusive" in str(err)
