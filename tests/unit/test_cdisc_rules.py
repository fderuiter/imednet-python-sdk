import pickle
import sys
from types import ModuleType

import imednet.validation.cdisc as cdisc


class FakeInMemoryCacheService:
    def __init__(self):
        self.data = []

    def add_all(self, data):
        self.data.extend(data)

    def get_all_by_prefix(self, prefix):
        return [r for r in self.data if r.get("key", "").startswith(prefix)]

    def get(self, key):
        for item in self.data:
            if item.get("key") == key:
                return item
        return None


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


class FakeLibraryMetadataContainer:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class FakeExternalDictionariesContainer:
    def __init__(self, dictionary_path_mapping=None):
        self.dictionary_path_mapping = dictionary_path_mapping or {}


class FakeDataServiceFactory:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_data_service(self, paths):
        return {"paths": paths, "kwargs": self.kwargs}


class FakeRulesEngine:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def validate_single_rule(self, rule, datasets):
        return {"AE": [{"violation": rule["core_id"]}]}


class FakeConditionCompositeFactory:
    @staticmethod
    def get_condition_composite(cond):
        return {"wrapped": cond}


class FakeRuleValidationResult:
    def __init__(self, rule, violations):
        self.rule = rule
        self.violations = violations


def _setup_cdisc(monkeypatch):
    _cre = ModuleType("cdisc_rules_engine")
    _services = ModuleType("cdisc_rules_engine.services")
    _cache_mod = ModuleType("cdisc_rules_engine.services.cache")
    _utilities = ModuleType("cdisc_rules_engine.utilities")
    _utils_mod = ModuleType("cdisc_rules_engine.utilities.utils")
    _models = ModuleType("cdisc_rules_engine.models")
    _rule_mod = ModuleType("cdisc_rules_engine.models.rule")
    _pandas_mod = ModuleType("cdisc_rules_engine.models.dataset.pandas_dataset")
    _dataset_var_mod = ModuleType("cdisc_rules_engine.models.dataset_variable")
    _meta_mod = ModuleType("cdisc_rules_engine.models.sdtm_dataset_metadata")
    _actions_mod = ModuleType("cdisc_rules_engine.models.actions")
    _lib_meta_mod = ModuleType("cdisc_rules_engine.models.library_metadata_container")
    _data_services_mod = ModuleType("cdisc_rules_engine.services.data_services")
    _config_mod = ModuleType("cdisc_rules_engine.config")
    _rules_engine_mod = ModuleType("cdisc_rules_engine.rules_engine")
    _cond_mod = ModuleType("cdisc_rules_engine.models.rule_conditions")
    _result_mod = ModuleType("cdisc_rules_engine.models.rule_validation_result")
    _ext_dict_mod = ModuleType("cdisc_rules_engine.models.external_dictionaries_container")
    _pyreadstat_mod = ModuleType("pyreadstat")

    _cache_mod.InMemoryCacheService = FakeInMemoryCacheService
    _services.cache = _cache_mod
    _cre.services = _services

    _utils_mod.get_rules_cache_key = get_rules_cache_key
    _utilities.utils = _utils_mod
    _cre.utilities = _utilities

    _rule_mod.Rule = FakeRule
    _models.rule = _rule_mod

    _pandas_mod.PandasDataset = FakePandasDataset
    _dataset_var_mod.DatasetVariable = FakeDatasetVariable
    _meta_mod.SDTMDatasetMetadata = FakeMetadata
    _actions_mod.COREActions = FakeCOREActions
    _lib_meta_mod.LibraryMetadataContainer = FakeLibraryMetadataContainer
    _ext_dict_mod.ExternalDictionariesContainer = FakeExternalDictionariesContainer
    _data_services_mod.DataServiceFactory = FakeDataServiceFactory
    _config_mod.config = {}
    _rules_engine_mod.RulesEngine = FakeRulesEngine
    _cond_mod.ConditionCompositeFactory = FakeConditionCompositeFactory
    _result_mod.RuleValidationResult = FakeRuleValidationResult

    def fake_read_xport(path):
        import pandas as pd

        return pd.DataFrame({"A": [1]}), type("Meta", (), {"file_label": "lbl"})

    _pyreadstat_mod.read_xport = fake_read_xport

    # stub business_rules.engine.run
    engine_mod = ModuleType("business_rules.engine")

    def fake_run(*, rule, defined_variables, defined_actions):
        defined_actions.output_container.append(rule)
        return True

    engine_mod.run = fake_run
    monkeypatch.setitem(sys.modules, "business_rules", ModuleType("business_rules"))
    monkeypatch.setitem(sys.modules, "business_rules.engine", engine_mod)

    _cre.models = _models

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

    monkeypatch.setitem(sys.modules, "cdisc_rules_engine", _cre)
    monkeypatch.setitem(sys.modules, "cdisc_rules_engine.services", _services)
    monkeypatch.setitem(sys.modules, "cdisc_rules_engine.services.cache", _cache_mod)
    monkeypatch.setitem(sys.modules, "cdisc_rules_engine.utilities", _utilities)
    monkeypatch.setitem(sys.modules, "cdisc_rules_engine.utilities.utils", _utils_mod)
    monkeypatch.setitem(sys.modules, "cdisc_rules_engine.models", _models)
    monkeypatch.setitem(sys.modules, "cdisc_rules_engine.models.rule", _rule_mod)
    monkeypatch.setitem(
        sys.modules,
        "cdisc_rules_engine.models.dataset.pandas_dataset",
        _pandas_mod,
    )
    monkeypatch.setitem(
        sys.modules,
        "cdisc_rules_engine.models.dataset_variable",
        _dataset_var_mod,
    )
    monkeypatch.setitem(
        sys.modules,
        "cdisc_rules_engine.models.sdtm_dataset_metadata",
        _meta_mod,
    )
    monkeypatch.setitem(sys.modules, "cdisc_rules_engine.models.actions", _actions_mod)
    monkeypatch.setitem(
        sys.modules,
        "cdisc_rules_engine.models.library_metadata_container",
        _lib_meta_mod,
    )
    monkeypatch.setitem(
        sys.modules,
        "cdisc_rules_engine.services.data_services",
        _data_services_mod,
    )
    monkeypatch.setitem(sys.modules, "cdisc_rules_engine.config", _config_mod)
    monkeypatch.setitem(sys.modules, "cdisc_rules_engine.rules_engine", _rules_engine_mod)
    monkeypatch.setitem(
        sys.modules,
        "cdisc_rules_engine.models.rule_conditions",
        _cond_mod,
    )
    monkeypatch.setitem(
        sys.modules,
        "cdisc_rules_engine.models.rule_validation_result",
        _result_mod,
    )
    monkeypatch.setitem(
        sys.modules,
        "cdisc_rules_engine.models.external_dictionaries_container",
        _ext_dict_mod,
    )
    monkeypatch.setitem(sys.modules, "pyreadstat", _pyreadstat_mod)
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


def test_create_dataset_metadata(tmp_path, monkeypatch):
    _setup_cdisc(monkeypatch)
    xpt = tmp_path / "ae.xpt"
    xpt.write_bytes(b"")
    meta = cdisc.create_dataset_metadata(str(xpt))
    assert meta.name == "AE"
    assert meta.filename == "ae.xpt"
    assert meta.record_count == 1


def test_get_datasets_metadata(tmp_path, monkeypatch):
    _setup_cdisc(monkeypatch)
    (tmp_path / "ae.xpt").write_bytes(b"")
    (tmp_path / "dm.xpt").write_bytes(b"")
    metas = cdisc.get_datasets_metadata(str(tmp_path))
    assert len(metas) == 2


def test_create_external_dictionaries_container(monkeypatch):
    _setup_cdisc(monkeypatch)
    paths = {"meddra": "/some/path"}
    container = cdisc.create_external_dictionaries_container(paths)
    assert container.dictionary_path_mapping == paths


def test_create_rules_engine_with_external_dicts(monkeypatch):
    _setup_cdisc(monkeypatch)
    ext = cdisc.create_external_dictionaries_container({"meddra": "/some"})
    engine = cdisc.create_rules_engine(
        cache=None,
        data_service=None,
        library_metadata=None,
        standard="sdtmig",
        standard_version="3-4",
        dataset_paths=[],
        external_dictionaries=ext,
    )
    assert engine.kwargs["external_dictionaries"] == ext


def test_validate_rules(monkeypatch):
    _setup_cdisc(monkeypatch)
    datasets = [object()]
    engine = cdisc.create_rules_engine(
        cache=None,
        data_service=None,
        library_metadata=None,
        standard="sdtmig",
        standard_version="3-4",
        dataset_paths=[],
    )
    rules = [{"core_id": "R1", "conditions": {"any": []}}]
    results = cdisc.validate_rules(engine, rules, datasets)
    assert results and results[0].violations


def test_write_validation_report(tmp_path, monkeypatch):
    _setup_cdisc(monkeypatch)
    result = cdisc.validate_rules(
        cdisc.create_rules_engine(
            cache=None,
            data_service=None,
            library_metadata=None,
            standard="sdtmig",
            standard_version="3-4",
            dataset_paths=[],
        ),
        [{"core_id": "R1", "conditions": {}}],
        [object()],
    )[0]
    out = tmp_path / "report.txt"
    cdisc.write_validation_report([result], str(out))
    text = out.read_text()
    assert "Rule: R1" in text
