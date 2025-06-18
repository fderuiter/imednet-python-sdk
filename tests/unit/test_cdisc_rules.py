import pickle
import sys
from types import ModuleType

import imednet.validation.cdisc as cdisc


def _setup_cdisc(monkeypatch):
    cre = ModuleType("cdisc_rules_engine")
    services = ModuleType("cdisc_rules_engine.services")
    cache_mod = ModuleType("cdisc_rules_engine.services.cache")
    utilities = ModuleType("cdisc_rules_engine.utilities")
    utils_mod = ModuleType("cdisc_rules_engine.utilities.utils")
    models = ModuleType("cdisc_rules_engine.models")
    rule_mod = ModuleType("cdisc_rules_engine.models.rule")
    pandas_mod = ModuleType("cdisc_rules_engine.models.dataset.pandas_dataset")
    dataset_var_mod = ModuleType("cdisc_rules_engine.models.dataset_variable")
    meta_mod = ModuleType("cdisc_rules_engine.models.sdtm_dataset_metadata")
    actions_mod = ModuleType("cdisc_rules_engine.models.actions")

    class FakeInMemoryCacheService:
        def __init__(self):
            self.data = []

        def add_all(self, data):
            self.data.extend(data)

        def get_all_by_prefix(self, prefix):
            return [r for r in self.data if r.get("key", "").startswith(prefix)]

    def get_rules_cache_key(std, ver):
        return f"{std}-{ver}"

    class FakeRule:
        def __init__(self, data):
            self.data = data

        @classmethod
        def from_cdisc_metadata(cls, meta):
            return {"core_id": meta["Core"]["Id"]}

    class FakePandasDataset:
        def __init__(self, data):
            self.data = data

    class FakeDatasetVariable:
        def __init__(self, dataset, column_prefix_map=None, **kwargs):
            self.dataset = dataset
            self.column_prefix_map = column_prefix_map or {}
            self.kwargs = kwargs

    class FakeMetadata:
        def __init__(self, name, label, first_record=None):
            self.name = name
            self.label = label
            self.first_record = first_record
            self.domain = name

    class FakeCOREActions:
        def __init__(self, output_container=None, **kwargs):
            self.output_container = output_container if output_container is not None else []

    cache_mod.InMemoryCacheService = FakeInMemoryCacheService
    services.cache = cache_mod
    cre.services = services

    utils_mod.get_rules_cache_key = get_rules_cache_key
    utilities.utils = utils_mod
    cre.utilities = utilities

    rule_mod.Rule = FakeRule
    models.rule = rule_mod

    pandas_mod.PandasDataset = FakePandasDataset
    dataset_var_mod.DatasetVariable = FakeDatasetVariable
    meta_mod.SDTMDatasetMetadata = FakeMetadata
    actions_mod.COREActions = FakeCOREActions

    # stub business_rules.engine.run
    engine_mod = ModuleType("business_rules.engine")

    def fake_run(*, rule, defined_variables, defined_actions):
        defined_actions.output_container.append(rule)
        return True

    engine_mod.run = fake_run
    monkeypatch.setitem(sys.modules, "business_rules", ModuleType("business_rules"))
    monkeypatch.setitem(sys.modules, "business_rules.engine", engine_mod)

    cre.models = models

    class DummyManager:
        _factory = None

        @classmethod
        def register(cls, name, factory):  # noqa: D401
            cls._factory = factory

        def start(self):
            pass

        def InMemoryCacheService(self):  # noqa: N802 - mimic actual name
            assert self._factory is not None
            return self._factory()

    monkeypatch.setitem(sys.modules, "cdisc_rules_engine", cre)
    monkeypatch.setitem(sys.modules, "cdisc_rules_engine.services", services)
    monkeypatch.setitem(sys.modules, "cdisc_rules_engine.services.cache", cache_mod)
    monkeypatch.setitem(sys.modules, "cdisc_rules_engine.utilities", utilities)
    monkeypatch.setitem(sys.modules, "cdisc_rules_engine.utilities.utils", utils_mod)
    monkeypatch.setitem(sys.modules, "cdisc_rules_engine.models", models)
    monkeypatch.setitem(sys.modules, "cdisc_rules_engine.models.rule", rule_mod)
    monkeypatch.setitem(
        sys.modules,
        "cdisc_rules_engine.models.dataset.pandas_dataset",
        pandas_mod,
    )
    monkeypatch.setitem(
        sys.modules,
        "cdisc_rules_engine.models.dataset_variable",
        dataset_var_mod,
    )
    monkeypatch.setitem(
        sys.modules,
        "cdisc_rules_engine.models.sdtm_dataset_metadata",
        meta_mod,
    )
    monkeypatch.setitem(sys.modules, "cdisc_rules_engine.models.actions", actions_mod)
    monkeypatch.setattr(cdisc, "SyncManager", DummyManager)


def test_load_rules_cache(tmp_path, monkeypatch):
    _setup_cdisc(monkeypatch)
    rules = [{"key": "sdtmig-3-4-1"}]
    with open(tmp_path / "rules.pkl", "wb") as f:
        pickle.dump(rules, f)

    cache = cdisc.load_rules_cache(str(tmp_path))
    assert cache.get_all_by_prefix("sdtmig") == rules


def test_get_rules(monkeypatch):
    _setup_cdisc(monkeypatch)
    from cdisc_rules_engine.services.cache import InMemoryCacheService

    cache = InMemoryCacheService()
    cache.add_all([{"key": "sdtmig-3-4-1"}, {"key": "adam-2-1"}])

    rules = cdisc.get_rules(cache, "sdtmig", "3.4")
    assert rules == [{"key": "sdtmig-3-4-1"}]


def test_rule_from_metadata(monkeypatch):
    _setup_cdisc(monkeypatch)
    rule = cdisc.rule_from_metadata({"Core": {"Id": "CORE-1"}})
    assert rule.data == {"core_id": "CORE-1"}


def test_dataset_variable_from_dataframe(monkeypatch):
    _setup_cdisc(monkeypatch)
    import pandas as pd

    df = pd.DataFrame({"AESEQ": [1]})
    dv, meta = cdisc.dataset_variable_from_dataframe(df, "AE")
    assert meta.name == "AE"
    assert dv.dataset.data.equals(df)


def test_run_business_rules(monkeypatch):
    _setup_cdisc(monkeypatch)
    import pandas as pd

    df = pd.DataFrame({"AESEQ": [1]})
    dv, meta = cdisc.dataset_variable_from_dataframe(df, "AE")
    rules = [{"core_id": "R1", "domains": {"Include": ["AE"]}}]
    results = cdisc.run_business_rules(rules, dv, meta)
    assert results  # results should not be empty
