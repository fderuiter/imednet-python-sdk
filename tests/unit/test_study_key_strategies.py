from imednet.core.endpoint.strategies import (
    KeepStudyKeyStrategy,
    OptionalStudyKeyStrategy,
    PopStudyKeyStrategy,
)


class TestKeepStudyKeyStrategy:
    def test_process_with_valid_key(self):
        strategy = KeepStudyKeyStrategy()
        filters = {"studyKey": "study-123", "other": "val"}
        key, new_filters = strategy.process(filters)
        assert key == "study-123"
        assert new_filters == filters

    def test_process_missing_key(self):
        strategy = KeepStudyKeyStrategy()
        filters = {"other": "val"}
        key, new_filters = strategy.process(filters)
        assert key is None
        assert new_filters == filters


class TestPopStudyKeyStrategy:
    def test_process_with_valid_key(self):
        strategy = PopStudyKeyStrategy()
        filters = {"studyKey": "study-123", "other": "val"}
        key, new_filters = strategy.process(filters)
        assert key == "study-123"
        assert new_filters == {"other": "val"}

    def test_process_missing_key(self):
        strategy = PopStudyKeyStrategy()
        filters = {"other": "val"}
        key, new_filters = strategy.process(filters)
        assert key is None
        assert new_filters == {"other": "val"}


class TestOptionalStudyKeyStrategy:
    def test_process_with_key(self):
        strategy = OptionalStudyKeyStrategy()
        filters = {"studyKey": "study-123", "other": "val"}
        key, new_filters = strategy.process(filters)
        assert key == "study-123"
        assert new_filters == filters

    def test_process_without_key(self):
        strategy = OptionalStudyKeyStrategy()
        filters = {"other": "val"}
        key, new_filters = strategy.process(filters)
        assert key is None
        assert new_filters == filters
