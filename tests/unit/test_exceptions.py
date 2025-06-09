from imednet.core.exceptions import ApiError


def test_api_error_str_includes_details():
    err = ApiError({"detail": "oops"}, status_code=404)
    text = str(err)
    assert "Status Code: 404" in text
    assert "{'detail': 'oops'}" in text
