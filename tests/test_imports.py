import imednet_py


def test_import() -> None:
    assert hasattr(imednet_py, "__version__")
