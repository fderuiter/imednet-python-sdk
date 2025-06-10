import importlib.resources
import json

from imednet.ui.desktop import CLI_COMMANDS

with importlib.resources.open_text("imednet.ui", "help.json") as fh:
    HELP_DATA = json.load(fh)


def test_all_commands_have_help() -> None:
    for cmd in CLI_COMMANDS:
        assert cmd in HELP_DATA
        assert HELP_DATA[cmd].get("description")
        for param in CLI_COMMANDS[cmd]["params"]:
            p_name = param["name"]
            assert p_name in HELP_DATA[cmd].get("params", {})
            p_help = HELP_DATA[cmd]["params"][p_name]
            assert p_help.get("type") or p_help.get("example")
