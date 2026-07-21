from scripts.ci_plan import parse_dependency_name


def test_parse_dependency_name_simple():
    assert parse_dependency_name("requests") == "requests"
    assert parse_dependency_name("imednet-workflows") == "imednet-workflows"
    assert parse_dependency_name("my.package_name-123") == "my.package_name-123"


def test_parse_dependency_name_with_version():
    assert parse_dependency_name("requests>=2.0.0") == "requests"
    assert parse_dependency_name("requests<=2.0.0") == "requests"
    assert parse_dependency_name("requests==2.0.0") == "requests"
    assert parse_dependency_name("requests~=2.0.0") == "requests"
    assert parse_dependency_name("requests!=2.0.0") == "requests"
    assert parse_dependency_name("requests > 2.0.0") == "requests"
    assert parse_dependency_name("imednet-workflows < 0.6.0") == "imednet-workflows"


def test_parse_dependency_name_with_extras():
    assert parse_dependency_name("requests[security]") == "requests"
    assert parse_dependency_name("requests[security,socks]") == "requests"
    assert parse_dependency_name("requests [security]") == "requests"


def test_parse_dependency_name_with_extras_and_version():
    assert parse_dependency_name("requests[security]>=2.0.0") == "requests"
    assert parse_dependency_name("requests[security,socks] == 2.0.0") == "requests"


def test_parse_dependency_name_with_environment_markers():
    assert parse_dependency_name("requests; python_version < '3.8'") == "requests"
    assert parse_dependency_name("requests ; python_version < '3.8'") == "requests"
    assert parse_dependency_name("requests>=2.0.0; sys_platform == 'win32'") == "requests"
    assert parse_dependency_name("requests[security]; sys_platform == 'win32'") == "requests"
    assert parse_dependency_name("requests[security]>=2.0.0; sys_platform == 'win32'") == "requests"


def test_parse_dependency_name_edge_cases():
    assert parse_dependency_name("  requests  ") == "requests"
    assert parse_dependency_name("A") == "A"
    assert parse_dependency_name("1") == "1"
    assert parse_dependency_name("foo.bar-baz_qux") == "foo.bar-baz_qux"
