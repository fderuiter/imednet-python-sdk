import pytest
from imednet.core.endpoint.strategies import (
    KeepStudyKeyStrategy,
    PopStudyKeyStrategy,
    OptionalStudyKeyStrategy,
)

class TestKeepStudyKeyStrategy:
    def test_process_with_valid_key(self):
        strategy = KeepStudyKeyStrategy()
        filters = {"studyKey": "valid-key", "other": "param"}
        key, new_filters = strategy.process(filters)

        assert key == "valid-key"
        assert "studyKey" in new_filters
        assert new_filters["studyKey"] == "valid-key"
        assert new_filters["other"] == "param"

    def test_process_missing_key_raises_error(self):
        strategy = KeepStudyKeyStrategy()
        filters = {"other": "param"}

        with pytest.raises(ValueError, match="Study key must be provided"):
            strategy.process(filters)

    def test_process_custom_exception(self):
        class CustomError(Exception):
            pass

        strategy = KeepStudyKeyStrategy(exception_cls=CustomError)
        filters = {"other": "param"}

        with pytest.raises(CustomError):
            strategy.process(filters)

    def test_process_empty_key_raises_error(self):
        strategy = KeepStudyKeyStrategy()
        filters = {"studyKey": "", "other": "param"}

        with pytest.raises(ValueError, match="Study key must be provided"):
            strategy.process(filters)


class TestPopStudyKeyStrategy:
    def test_process_with_valid_key(self):
        strategy = PopStudyKeyStrategy()
        filters = {"studyKey": "valid-key", "other": "param"}
        key, new_filters = strategy.process(filters)

        assert key == "valid-key"
        assert "studyKey" not in new_filters
        assert new_filters["other"] == "param"

    def test_process_missing_key_raises_error(self):
        strategy = PopStudyKeyStrategy()
        filters = {"other": "param"}

        with pytest.raises(ValueError, match="Study key must be provided"):
            strategy.process(filters)

    def test_process_custom_exception(self):
        class CustomError(Exception):
            pass

        strategy = PopStudyKeyStrategy(exception_cls=CustomError)
        filters = {"other": "param"}

        with pytest.raises(CustomError):
            strategy.process(filters)

    def test_process_empty_key_returns_empty_string(self):
        strategy = PopStudyKeyStrategy()
        filters = {"studyKey": "", "other": "param"}
        key, new_filters = strategy.process(filters)
        assert key == ""
        assert "studyKey" not in new_filters


class TestOptionalStudyKeyStrategy:
    def test_process_with_key(self):
        strategy = OptionalStudyKeyStrategy()
        filters = {"studyKey": "valid-key", "other": "param"}
        key, new_filters = strategy.process(filters)

        assert key == "valid-key"
        assert "studyKey" in new_filters
        assert new_filters["studyKey"] == "valid-key"

    def test_process_without_key(self):
        strategy = OptionalStudyKeyStrategy()
        filters = {"other": "param"}
        key, new_filters = strategy.process(filters)

        assert key is None
        assert "studyKey" not in new_filters
        assert new_filters["other"] == "param"
