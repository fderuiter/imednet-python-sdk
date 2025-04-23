def test_smoke_import() -> None:
    import imednet

    assert hasattr(imednet, "ImednetSDK")
