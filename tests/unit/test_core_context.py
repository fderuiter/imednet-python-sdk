from imednet.core.context import Context


def test_set_and_clear_default_study_key() -> None:
    ctx = Context()
    ctx.set_default_study_key("S1")
    assert ctx.default_study_key == "S1"
    ctx.clear_default_study_key()
    assert ctx.default_study_key is None
