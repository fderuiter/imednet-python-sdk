from imednet import errors


def test_api_error_str_includes_details() -> None:
    err = errors.ApiError({"msg": "bad"}, status_code=400)
    text = str(err)
    assert "Status Code: 400" in text
    assert "msg" in text


def test_exception_hierarchy() -> None:
    assert issubclass(errors.AuthenticationError, errors.ApiError)
    assert issubclass(errors.AuthorizationError, errors.ApiError)
    assert issubclass(errors.NotFoundError, errors.ApiError)
    assert issubclass(errors.RateLimitError, errors.ApiError)
    assert issubclass(errors.ServerError, errors.ApiError)
    assert issubclass(errors.ValidationError, errors.ApiError)

    # New check
    assert issubclass(errors.ClientError, errors.ImednetError)
