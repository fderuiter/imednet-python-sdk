from imednet.core.exceptions import (
    ApiError,
    AuthenticationError,
    AuthorizationError,
    ImednetError,
    NotFoundError,
    RateLimitError,
    RequestError,
    ServerError,
    ValidationError,
)


def test_imednet_error_inheritance():
    assert issubclass(ImednetError, Exception)


def test_request_error_inheritance():
    assert issubclass(RequestError, ImednetError)


def test_api_error_inheritance():
    assert issubclass(ApiError, ImednetError)


def test_specific_errors_inheritance():
    assert issubclass(AuthenticationError, ApiError)
    assert issubclass(AuthorizationError, ApiError)
    assert issubclass(NotFoundError, ApiError)
    assert issubclass(RateLimitError, ApiError)
    assert issubclass(ServerError, ApiError)
    assert issubclass(ValidationError, ApiError)


def test_api_error_initialization():
    response = {"error": "Test error"}
    status_code = 400
    error = ApiError(response, status_code, code="E1", message="boom", field="x")

    assert error.response == response
    assert error.status_code == status_code
    assert error.code == "E1"
    assert error.message == "boom"
    assert error.field == "x"


def test_api_error_str_with_status_and_response():
    response = {"error": "Test error"}
    status_code = 400
    error = ApiError(response, status_code)

    error_str = str(error)
    assert "{'error': 'Test error'}" in error_str
    assert "Status Code: 400" in error_str


def test_api_error_str_with_response_only():
    response = {"error": "Test error"}
    error = ApiError(response)

    error_str = str(error)
    assert "{'error': 'Test error'}" in error_str
    assert "Status Code:" not in error_str


def test_api_error_str_with_status_only():
    error = ApiError(None, 400)

    error_str = str(error)
    assert "Status Code: 400" in error_str
    assert "Response:" not in error_str


def test_api_error_str_without_details():
    error = ApiError(None)

    error_str = str(error)
    assert error_str == "None"
