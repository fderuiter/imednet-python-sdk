from imednet.core import exceptions


def test_api_error_str_includes_details() -> None:
    err = exceptions.ApiError({"msg": "bad"}, status_code=400)
    text = str(err)
    assert "Status Code: 400" in text
    assert "msg" in text


def test_exception_hierarchy() -> None:
    assert issubclass(exceptions.AuthenticationError, exceptions.ApiError)
    assert issubclass(exceptions.AuthorizationError, exceptions.ApiError)
    assert issubclass(exceptions.NotFoundError, exceptions.ApiError)
    assert issubclass(exceptions.RateLimitError, exceptions.ApiError)
    assert issubclass(exceptions.ServerError, exceptions.ApiError)
    assert issubclass(exceptions.ValidationError, exceptions.ApiError)
