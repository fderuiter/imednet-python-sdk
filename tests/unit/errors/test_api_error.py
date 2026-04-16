from imednet.errors.api import ApiError


def test_api_error_str_representation():
    # Test basic instantiation with string
    err = ApiError("Something went wrong")
    assert str(err) == "Something went wrong (Response: Something went wrong)"

    # Test with status code
    err2 = ApiError("Not Found", status_code=404)
    assert str(err2) == "Not Found (Status Code: 404, Response: Not Found)"

    # Test with dictionary response
    err3 = ApiError({"error": "Bad Request"}, status_code=400)
    assert str(err3) == (
        "{'error': 'Bad Request'} " "(Status Code: 400, Response: {'error': 'Bad Request'})"
    )


def test_api_error_empty_response():
    # Test instantiation with empty response string
    err = ApiError("", status_code=500)
    assert str(err) == " (Status Code: 500)"

    # Test instantiation with None response
    err2 = ApiError(None, status_code=500)
    assert str(err2) == "None (Status Code: 500)"


def test_api_error_base_str_only():
    err = ApiError(None)
    assert str(err) == "None"
