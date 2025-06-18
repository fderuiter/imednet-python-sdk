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


__all__ = [
    "load_rules_cache",
    "get_rules",
    "rule_from_metadata",
    "dataset_variable_from_dataframe",
    "run_business_rules",
]
