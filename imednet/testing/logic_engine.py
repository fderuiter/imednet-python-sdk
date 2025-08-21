from __future__ import annotations

from typing import Any, Dict, List

from imednet.testing.logic_parser import (
    Action,
    And,
    BusinessRule,
    Checked,
    Condition,
    Equals,
    Not,
    Or,
    TrueCondition,
)


class LogicEngine:
    """Evaluates business logic rules against record data."""

    def __init__(self, rules: List[BusinessRule]):
        self.rules = rules

    def evaluate(self, data: Dict[str, Any]) -> List[Action]:
        """
        Evaluates all business rules against the given data.

        Args:
            data: The current record data.

        Returns:
            A list of actions to be performed.
        """
        actions_to_perform = []
        for rule in self.rules:
            if self._evaluate_condition(rule.conditions, data):
                actions_to_perform.extend(rule.actions)
        return actions_to_perform

    def _evaluate_condition(self, condition: Condition, data: Dict[str, Any]) -> bool:
        """Recursively evaluates a single condition."""
        if isinstance(condition, And):
            return all(self._evaluate_condition(c, data) for c in condition.conditions)
        if isinstance(condition, Or):
            return any(self._evaluate_condition(c, data) for c in condition.conditions)
        if isinstance(condition, Not):
            return not self._evaluate_condition(condition.condition, data)
        if isinstance(condition, Equals):
            return data.get(condition.question) == condition.value
        if isinstance(condition, Checked):
            return data.get(condition.question) == "1"
        if isinstance(condition, TrueCondition):
            return True

        raise TypeError(f"Unknown condition type: {type(condition)}")
