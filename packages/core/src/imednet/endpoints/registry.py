"""Registry for all available API endpoints.

This module dynamically discovers and generates endpoint implementations
based on the centralized resource manifest.
"""

from __future__ import annotations

import json
import os
import importlib
from typing import Mapping, Type, Dict, Any

from imednet.core.endpoint.base import GenericEndpoint
from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.core.endpoint.strategies import PopStudyKeyStrategy, MappingParamProcessor
from imednet.core.paginator import AsyncJsonListPaginator, JsonListPaginator
from imednet.models.engine import ModelEngine

_ENDPOINT_REGISTRY: Dict[str, Type[GenericEndpoint]] = {}
_ASYNC_ENDPOINT_REGISTRY: Dict[str, Type[GenericEndpoint]] = {}

def _load_manifest() -> Dict[str, Any]:
    manifest_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "manifest.json"
    )
    if not os.path.exists(manifest_path):
        return {}
    with open(manifest_path, "r") as f:
        return json.load(f)

def _build_endpoints() -> None:
    manifest = _load_manifest()
    
    for resource_name, config in manifest.items():
        # Import model from spi.models to ensure type match
        try:
            models_mod = importlib.import_module("imednet.spi.models")
            model_cls = getattr(models_mod, config["model"])
        except (ImportError, AttributeError):
            model_cls = ModelEngine.get_model(config["model"])
            
        # Build OperationDef
        op_def_attrs = {
            "PATH": config.get("path", resource_name),
            "MODEL": model_cls,
            "_id_param": config.get("id_param"),
        }
        
        if "requires_study_key" in config:
            op_def_attrs["requires_study_key"] = config["requires_study_key"]
            
        if "page_size" in config:
            op_def_attrs["PAGE_SIZE"] = config["page_size"]
            
        if config.get("study_key_strategy") == "pop":
            op_def_attrs["STUDY_KEY_STRATEGY"] = PopStudyKeyStrategy()
            
        if "param_processor" in config:
            proc_config = config["param_processor"]
            op_def_attrs["PARAM_PROCESSOR"] = MappingParamProcessor(
                mapping=proc_config.get("mapping"),
                defaults=proc_config.get("defaults")
            )
            
        if "paginator" in config:
            if config["paginator"] == "JsonListPaginator":
                op_def_attrs["PAGINATOR_CLS"] = JsonListPaginator
                
        if "async_paginator" in config:
            if config["async_paginator"] == "AsyncJsonListPaginator":
                op_def_attrs["ASYNC_PAGINATOR_CLS"] = AsyncJsonListPaginator

        class_name_base = resource_name.replace("_", " ").title().replace(" ", "")
        
        OpDefClass = type(f"{class_name_base}OperationDef", (object,), op_def_attrs)
        
        # Base mixes
        sync_bases = [OpDefClass, EdcSyncListGetEndpoint]
        async_bases = [OpDefClass, EdcAsyncListGetEndpoint]
        
        if "custom_mixin" in config:
            module_name, class_name = config["custom_mixin"].rsplit(".", 1)
            try:
                mod = importlib.import_module(module_name)
                mixin_cls = getattr(mod, class_name)
                sync_bases.insert(0, mixin_cls)
            except Exception:
                pass
                
        if "async_custom_mixin" in config:
            module_name, class_name = config["async_custom_mixin"].rsplit(".", 1)
            try:
                mod = importlib.import_module(module_name)
                mixin_cls = getattr(mod, class_name)
                async_bases.insert(0, mixin_cls)
            except Exception:
                pass

        # Create the dynamic classes
        SyncClass = type(f"{class_name_base}Endpoint", tuple(sync_bases), {})
        AsyncClass = type(f"Async{class_name_base}Endpoint", tuple(async_bases), {})
        
        _ENDPOINT_REGISTRY[resource_name] = SyncClass
        _ASYNC_ENDPOINT_REGISTRY[resource_name] = AsyncClass

_build_endpoints()

ENDPOINT_REGISTRY: Mapping[str, Type[GenericEndpoint]] = _ENDPOINT_REGISTRY
ASYNC_ENDPOINT_REGISTRY: Mapping[str, Type[GenericEndpoint]] = _ASYNC_ENDPOINT_REGISTRY
