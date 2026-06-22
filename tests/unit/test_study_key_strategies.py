"""TODO: Add docstring."""
from imednet.core.endpoint.strategies import (
    KeepStudyKeyStrategy,
    OptionalStudyKeyStrategy,
    PopStudyKeyStrategy,
)


class TestKeepStudyKeyStrategy:
    """TODO: Add docstring."""
    def test_process_with_valid_key(self):
        """TODO: Add docstring."""
        strategy = KeepStudyKeyStrategy()
        filters = {"studyKey": "study-123", "other": "val"}
        key, new_filters = strategy.process(filters)
        assert key == "study-123"
        assert new_filters == filters

    def test_process_missing_key(self):
        """TODO: Add docstring."""
        strategy = KeepStudyKeyStrategy()
        filters = {"other": "val"}
        key, new_filters = strategy.process(filters)
        assert key is None
        assert new_filters == filters


class TestPopStudyKeyStrategy:
    """TODO: Add docstring."""
    def test_process_with_valid_key(self):
        """TODO: Add docstring."""
        strategy = PopStudyKeyStrategy()
        filters = {"studyKey": "study-123", "other": "val"}
        key, new_filters = strategy.process(filters)
        assert key == "study-123"
        assert new_filters == {"other": "val"}

    def test_process_missing_key(self):
        """TODO: Add docstring."""
        strategy = PopStudyKeyStrategy()
        filters = {"other": "val"}
        key, new_filters = strategy.process(filters)
        assert key is None
        assert new_filters == {"other": "val"}


class TestOptionalStudyKeyStrategy:
    """TODO: Add docstring."""
    def test_process_with_key(self):
        """TODO: Add docstring."""
        strategy = OptionalStudyKeyStrategy()
        filters = {"studyKey": "study-123", "other": "val"}
        key, new_filters = strategy.process(filters)
        assert key == "study-123"
        assert new_filters == filters

    def test_process_without_key(self):
        """TODO: Add docstring."""
        strategy = OptionalStudyKeyStrategy()
        filters = {"other": "val"}
        key, new_filters = strategy.process(filters)
        assert key is None
        assert new_filters == filters
