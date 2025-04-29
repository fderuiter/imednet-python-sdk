from imednet.utils.filters import build_filter_string


def test_single_equality_filter():
    assert build_filter_string({"status": "active"}) == "status==active"


def test_multiple_equality_filters():
    result = build_filter_string({"status": "active", "age": 30})
    assert ("status==active;age==30" == result) or ("age==30;status==active" == result)


def test_tuple_operator_filter():
    assert build_filter_string({"age": (">", 18)}) == "age>18"


def test_list_or_filter():
    assert build_filter_string({"type": ["A", "B"]}) == "type==A,type==B"


def test_mixed_filters():
    filters = {"age": (">=", 21), "status": "active", "type": ["A", "B"]}
    result = build_filter_string(filters)
    # Order is not guaranteed, so check all possible combinations
    expected_parts = ["age>=21", "status==active", "type==A,type==B"]
    for part in expected_parts:
        assert part in result
    assert result.count(";") == 2


def test_custom_connectors():
    filters = {"a": 1, "b": ["x", "y"]}
    result = build_filter_string(filters, and_connector="&", or_connector="|")
    # 'a==1&b==x|b==y' or 'b==x|b==y&a==1'
    assert "a==1" in result
    assert "b==x|b==y" in result
    assert "&" in result


def test_empty_filters():
    assert build_filter_string({}) == ""


def test_list_single_value():
    assert build_filter_string({"foo": ["bar"]}) == "foo==bar"


def test_tuple_custom_operator():
    assert build_filter_string({"name": ("=~", "John")}) == "name=~John"
