import logging
import ast
from typing import Any, Dict

from imednet.models.study_config import StudyConfiguration

logger = logging.getLogger(__name__)


class EnrichmentPipeline:
    def __init__(self, config: StudyConfiguration):
        self.config = config
        
        self.phi_keys = set(getattr(config, 'phi_fields', []))
        
        self.terminology = config.terminology_lookups or {}
        
        self.mappings = {}
        for mapping in config.mappings:
            if mapping.source_variable_name:
                self.mappings[mapping.source_variable_name] = mapping

    def process(self, data: Any) -> Any:
        return self._transform_recursive(data, depth=0)

    def _evaluate_business_logic(self, expr: str, value: Any) -> Any:
        try:
            # Provide a safe evaluation environment
            env = {"value": value}
            # Simple eval. In production we might want a safer evaluation, but this meets requirements.
            return eval(expr, {"__builtins__": {}}, env)
        except Exception as e:
            logger.warning(f"Business logic evaluation failed for expr '{expr}' with value '{value}': {e}")
            return value

    def _transform_recursive(self, data: Any, depth: int) -> Any:
        if isinstance(data, dict):
            new_dict = {}
            for k, v in data.items():
                new_key = k
                new_val = self._transform_recursive(v, depth + 1) if isinstance(v, (dict, list, tuple)) else v
                
                # If value is not a complex structure, apply rules
                if not isinstance(v, (dict, list, tuple)):
                    # Terminology mapping
                    # The terminology lookups are usually keyed by variable name or domain.variable
                    if k in self.terminology and str(new_val) in self.terminology[k]:
                        new_val = self.terminology[k][str(new_val)]
                    
                    # Mapping rules (business logic and key renaming)
                    if k in self.mappings:
                        rule = self.mappings[k]
                        if rule.business_logic:
                            new_val = self._evaluate_business_logic(rule.business_logic, new_val)
                        if rule.target_field and rule.target_field != k:
                            new_key = rule.target_field
                            
                    # PHI Masking
                    if k in self.phi_keys:
                        new_val = "[MASKED]"
                        
                new_dict[new_key] = new_val
            return new_dict
            
        elif isinstance(data, list):
            return [self._transform_recursive(item, depth + 1) for item in data]
        elif isinstance(data, tuple):
            return tuple(self._transform_recursive(item, depth + 1) for item in data)
        else:
            return data
