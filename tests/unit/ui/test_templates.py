from pathlib import Path

from imednet.ui.template_manager import TemplateManager


def test_template_crud(tmp_path: Path) -> None:
    path = tmp_path / "templates.json"
    mgr = TemplateManager(path=path)

    mgr.save("t1", {"a": "1"})
    assert mgr.load("t1") == {"a": "1"}
    assert mgr.list() == ["t1"]

    mgr.rename("t1", "t2")
    assert mgr.load("t2") == {"a": "1"}

    mgr.delete("t2")
    assert mgr.list() == []
