from __future__ import annotations

import os
import pathlib
import pickle
from multiprocessing import freeze_support
from multiprocessing.managers import SyncManager

import pyreadstat
from business_rules.engine import run
from cdisc_rules_engine.models.actions import COREActions
from cdisc_rules_engine.models.dataset.pandas_dataset import PandasDataset
from cdisc_rules_engine.models.dataset_variable import DatasetVariable
from cdisc_rules_engine.models.sdtm_dataset_metadata import SDTMDatasetMetadata
from cdisc_rules_engine.services.cache import InMemoryCacheService
from cdisc_rules_engine.utilities.utils import get_rules_cache_key


class CacheManager(SyncManager):
    pass


CacheManager.register("InMemoryCacheService", InMemoryCacheService)


def load_rules_cache(path_to_rules_cache: str):
    """Return an in-memory cache populated from ``path_to_rules_cache``."""
    cache_path = pathlib.Path(path_to_rules_cache)
    manager = CacheManager()
    manager.start()
    cache = manager.InMemoryCacheService()  # type: ignore[attr-defined]

    files = next(os.walk(cache_path), (None, None, []))[2]
    for fname in files:
        with open(cache_path / fname, "rb") as f:
            cache.add_all(pickle.load(f))
    return cache


def main() -> None:
    current_dir = os.getcwd()
    cache_path = os.path.join(current_dir, "cache")
    ae_file_path = os.path.join(current_dir, "ae.xpt")

    cache = load_rules_cache(cache_path)
    key_prefix = get_rules_cache_key("sdtmig", "3-4")
    rules = cache.get_all_by_prefix(key_prefix)

    ae_data, meta = pyreadstat.read_xport(ae_file_path)
    pandas_dataset = PandasDataset(data=ae_data)
    metadata = SDTMDatasetMetadata(
        name="AE",
        label=getattr(meta, "file_label", "Adverse Events"),
        first_record=ae_data.iloc[0].to_dict() if not ae_data.empty else None,
    )
    dataset_variable = DatasetVariable(
        pandas_dataset,
        column_prefix_map={"--": metadata.domain},
    )

    ae_rules = [
        r
        for r in rules
        if "AE" in r.get("domains", {}).get("Include", [])
        or "ALL" in r.get("domains", {}).get("Include", [])
    ]

    all_results: list[dict] = []
    for rule in ae_rules:
        results: list[dict] = []
        actions = COREActions(
            output_container=results,
            variable=dataset_variable,
            dataset_metadata=metadata,
            rule=rule,
            value_level_metadata=None,
        )
        triggered = run(
            rule=rule,
            defined_variables=dataset_variable,
            defined_actions=actions,
        )
        if triggered and results:
            all_results.extend(results)

    print("===== VALIDATION SUMMARY =====")
    print(f"Total rules checked: {len(ae_rules)}")
    print(f"Total issues found: {len(all_results)}")


if __name__ == "__main__":
    freeze_support()
    main()
