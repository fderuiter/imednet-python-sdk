"""Utilities for working with the CDISC Rules Engine."""

from __future__ import annotations

import os
import pathlib
import pickle
from multiprocessing.managers import SyncManager
from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:  # pragma: no cover - imported for type checking only
    import pandas as pd


def load_rules_cache(path_to_rules_cache: str) -> Any:
    """Load CDISC rule definitions from ``path_to_rules_cache``.

    Parameters
    ----------
    path_to_rules_cache:
        Directory containing pickled rule files as distributed with the
        ``cdisc-rules-engine`` package.
    """
    from cdisc_rules_engine.services.cache import InMemoryCacheService

    class CacheManager(SyncManager):
        pass

    CacheManager.register("InMemoryCacheService", InMemoryCacheService)

    cache_path = pathlib.Path(path_to_rules_cache)
    manager = CacheManager()
    manager.start()
    cache: Any = manager.InMemoryCacheService()  # type: ignore[attr-defined]

    files = next(os.walk(cache_path), (None, None, []))[2]
    for fname in files:
        with open(cache_path / fname, "rb") as f:
            cache.add_all(pickle.load(f))

    return cache


def get_rules(cache: Any, standard: str, version: str) -> List[dict]:
    """Return rules for the given standard and version from ``cache``."""
    from cdisc_rules_engine.utilities.utils import get_rules_cache_key

    cache_key_prefix = get_rules_cache_key(standard, version.replace(".", "-"))
    return cache.get_all_by_prefix(cache_key_prefix)


def rule_from_metadata(rule_metadata: dict) -> Any:
    """Construct a ``Rule`` object from CDISC rule metadata."""
    from cdisc_rules_engine.models.rule import Rule

    rule_dict = Rule.from_cdisc_metadata(rule_metadata)
    return Rule(rule_dict)


def dataset_variable_from_dataframe(
    data: "pd.DataFrame", domain: str, label: str | None = None
) -> tuple[Any, Any]:
    """Return a dataset variable and metadata for ``data``.

    Parameters
    ----------
    data:
        Dataframe containing the dataset to validate.
    domain:
        Dataset domain name (e.g. "AE").
    label:
        Optional human readable label for the dataset.
    """
    import pandas as pd
    from cdisc_rules_engine.models.dataset.pandas_dataset import PandasDataset
    from cdisc_rules_engine.models.dataset_variable import DatasetVariable
    from cdisc_rules_engine.models.sdtm_dataset_metadata import SDTMDatasetMetadata

    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")

    pandas_dataset = PandasDataset(data=data)
    metadata = SDTMDatasetMetadata(
        name=domain,
        label=label or domain,
        first_record=data.iloc[0].to_dict() if not data.empty else None,
    )
    dataset_variable = DatasetVariable(
        pandas_dataset,
        column_prefix_map={"--": metadata.domain},
    )
    return dataset_variable, metadata


def run_business_rules(
    rules: List[dict],
    dataset_variable: Any,
    dataset_metadata: Any,
    *,
    value_level_metadata: Any | None = None,
) -> List[Any]:
    """Execute business rules against ``dataset_variable``.

    Returns a list of results from triggered rules.
    """
    from business_rules.engine import run
    from cdisc_rules_engine.models.actions import COREActions

    all_results: List[Any] = []
    for rule in rules:
        results: list[Any] = []
        actions = COREActions(
            output_container=results,
            variable=dataset_variable,
            dataset_metadata=dataset_metadata,
            rule=rule,
            value_level_metadata=value_level_metadata,
        )
        try:
            triggered = run(
                rule=rule,
                defined_variables=dataset_variable,
                defined_actions=actions,
            )
        except Exception:
            continue
        if triggered and results:
            all_results.extend(results)
    return all_results


# Option B helpers


def create_dataset_metadata(file_path: str) -> Any:
    """Create dataset metadata from an XPT file."""
    import pyreadstat
    from cdisc_rules_engine.models.sdtm_dataset_metadata import SDTMDatasetMetadata

    try:
        data, meta = pyreadstat.read_xport(file_path)
        first_record = data.iloc[0].to_dict() if not data.empty else None
        kwargs = {
            "name": os.path.basename(file_path).split(".")[0].upper(),
            "label": getattr(meta, "file_label", ""),
            "filename": os.path.basename(file_path),
            "full_path": file_path,
            "file_size": os.path.getsize(file_path),
            "record_count": len(data),
            "first_record": first_record,
        }
        try:
            return SDTMDatasetMetadata(**kwargs)
        except TypeError:
            meta_obj = SDTMDatasetMetadata(
                kwargs["name"], kwargs["label"], first_record=kwargs["first_record"]
            )
            for key in ["filename", "full_path", "file_size", "record_count"]:
                setattr(meta_obj, key, kwargs[key])
            return meta_obj
    except Exception:
        return None


def get_datasets_metadata(directory: str) -> List[Any]:
    """Return list of metadata objects for all XPT files in ``directory``."""

    datasets: List[Any] = []
    for file in os.listdir(directory):
        if file.lower().endswith(".xpt"):
            file_path = os.path.join(directory, file)
            meta = create_dataset_metadata(file_path)
            if meta:
                datasets.append(meta)
    return datasets


def build_library_metadata(
    cache: Any,
    standard: str,
    standard_version: str,
    standard_substandard: str | None = None,
    ct_packages: List[str] | None = None,
) -> Any:
    """Create a library metadata container from ``cache``."""
    from cdisc_rules_engine.models.library_metadata_container import (
        LibraryMetadataContainer,
    )
    from cdisc_rules_engine.utilities.utils import (
        get_library_variables_metadata_cache_key,
        get_model_details_cache_key_from_ig,
        get_standard_details_cache_key,
        get_variable_codelist_map_cache_key,
    )

    standard_details_cache_key = get_standard_details_cache_key(
        standard, standard_version, standard_substandard
    )
    variable_details_cache_key = get_library_variables_metadata_cache_key(
        standard, standard_version, standard_substandard
    )

    standard_metadata = cache.get(standard_details_cache_key)
    model_metadata = {}
    if standard_metadata:
        model_cache_key = get_model_details_cache_key_from_ig(standard_metadata)
        model_metadata = cache.get(model_cache_key)

    variable_codelist_cache_key = get_variable_codelist_map_cache_key(
        standard, standard_version, standard_substandard
    )

    ct_package_metadata = {pkg: cache.get(pkg) for pkg in (ct_packages or [])}

    return LibraryMetadataContainer(
        standard_metadata=standard_metadata,
        model_metadata=model_metadata,
        variables_metadata=cache.get(variable_details_cache_key),
        variable_codelist_map=cache.get(variable_codelist_cache_key),
        ct_package_metadata=ct_package_metadata,
    )


def get_data_service(
    dataset_paths: List[str],
    cache: Any,
    standard: str,
    standard_version: str,
    standard_substandard: str | None,
    library_metadata: Any,
    max_dataset_size: int,
) -> Any:
    """Return a data service for the given dataset paths."""
    from cdisc_rules_engine.config import config as default_config
    from cdisc_rules_engine.services.data_services import DataServiceFactory

    factory = DataServiceFactory(
        config=default_config,
        cache_service=cache,
        standard=standard,
        standard_version=standard_version,
        standard_substandard=standard_substandard,
        library_metadata=library_metadata,
        max_dataset_size=max_dataset_size,
    )
    return factory.get_data_service(dataset_paths)


def create_rules_engine(
    cache: Any,
    data_service: Any,
    library_metadata: Any,
    standard: str,
    standard_version: str,
    dataset_paths: List[str],
    *,
    ct_packages: List[str] | None = None,
    define_xml_path: str | None = None,
    validate_xml: bool = False,
    standard_substandard: str | None = None,
    max_dataset_size: int = 0,
) -> Any:
    """Instantiate a ``RulesEngine`` for validation."""
    from cdisc_rules_engine.config import config as default_config
    from cdisc_rules_engine.rules_engine import RulesEngine

    return RulesEngine(
        cache=cache,
        data_service=data_service,
        config_obj=default_config,
        external_dictionaries=None,
        standard=standard,
        standard_version=standard_version,
        standard_substandard=standard_substandard,
        library_metadata=library_metadata,
        max_dataset_size=max_dataset_size,
        dataset_paths=dataset_paths,
        ct_packages=ct_packages,
        define_xml_path=define_xml_path,
        validate_xml=validate_xml,
    )


def validate_rules(rules_engine: Any, rules: List[dict], datasets: List[Any]) -> List[Any]:
    """Validate each rule against ``datasets`` using ``rules_engine``."""
    from cdisc_rules_engine.models.rule_conditions import ConditionCompositeFactory
    from cdisc_rules_engine.models.rule_validation_result import RuleValidationResult

    results: List[Any] = []
    for rule in rules:
        if isinstance(rule.get("conditions"), dict):
            rule["conditions"] = ConditionCompositeFactory.get_condition_composite(
                rule["conditions"]
            )
        domain_results = rules_engine.validate_single_rule(rule, datasets)
        flattened: List[Any] = []
        for domain in domain_results.values():
            flattened.extend(domain)
        results.append(RuleValidationResult(rule, flattened))
    return results


def write_validation_report(validation_results: List[Any], output_file: str) -> None:
    """Write ``validation_results`` to ``output_file``."""
    import json

    with open(output_file, "w") as f:
        for result in validation_results:
            rule_id = result.rule.get("core_id", "Unknown")
            f.write(f"Rule: {rule_id}\n")
            violations = getattr(result, "violations", None)
            if violations:
                f.write(f"Found {len(violations)} violations\n")
                for v in violations:
                    f.write(f"  - {json.dumps(v, default=str)}\n")
            else:
                f.write("  No violations found\n")
            f.write("\n")


__all__ = [
    "load_rules_cache",
    "get_rules",
    "rule_from_metadata",
    "dataset_variable_from_dataframe",
    "run_business_rules",
    "create_dataset_metadata",
    "get_datasets_metadata",
    "build_library_metadata",
    "get_data_service",
    "create_rules_engine",
    "validate_rules",
    "write_validation_report",
]
