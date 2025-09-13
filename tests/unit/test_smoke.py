def test_smoke_import() -> None:
    import imednet

    assert hasattr(imednet, "ImednetSDK")


def test_role_import() -> None:
    from imednet.api.models import Role

    assert Role.__name__ == "Role"
