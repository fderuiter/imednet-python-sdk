from imednet.utils.security import sanitize_csv_formula


def test_sanitize_csv_formula_unsafe():
    unsafe = ["=SUM(A1:A2)", "+1", "-1", "@foo"]
    for u in unsafe:
        assert sanitize_csv_formula(u) == f"'{u}"


def test_sanitize_csv_formula_safe():
    safe = ["hello", "123", "", None, 1, 1.5, True]
    for s in safe:
        assert sanitize_csv_formula(s) == s


def test_sanitize_csv_formula_mixed():
    # Should not touch values that don't start with trigger chars
    assert sanitize_csv_formula("foo=bar") == "foo=bar"
