from imednet.ui.desktop import CLI_COMMANDS, _parse_filter_string


def test_cli_commands_contains_known() -> None:
    assert "studies.list" in CLI_COMMANDS
    assert "workflows.extract-records" in CLI_COMMANDS


def test_parse_filter_string() -> None:
    assert _parse_filter_string("a=1,b=2") == {"a": "1", "b": "2"}
    assert _parse_filter_string("") is None
