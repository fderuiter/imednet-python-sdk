from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from imednet.testing.logic_parser import (
    Action,
    And,
    BusinessRule,
    Checked,
    Condition,
    DisableAndClearField,
    DisableField,
    Equals,
    GreaterThan,
    HideAndClearField,
    HideField,
    IsBlank,
    LessThan,
    Not,
    Or,
    TrueCondition,
)


class LogicEngine:
    """Evaluates business logic rules against record data."""

    def __init__(self, rules: List[BusinessRule]):
        self.rules = rules

    def _attempt_conversion(self, value: str | None) -> Any:
        """Attempts to convert a string to a float or date."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            pass
        try:
            # The format is DD-MMM-YYYY, e.g., 01-JAN-2024
            return datetime.strptime(value, "%d-%b-%Y").date()
        except (ValueError, TypeError):
            pass
        return value

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

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates all business rules and executes the resulting actions on the data.

        Args:
            data: The current record data, which will be modified in place.

        Returns:
            The modified data dictionary.
        """
        actions_to_perform = self.evaluate(data)

        for action in actions_to_perform:
            if isinstance(action, (DisableAndClearField, HideAndClearField)):
                if action.question in data:
                    data[action.question] = ""
            elif isinstance(action, (DisableField, HideField)):
                # These actions relate to UI state and have no effect on the data dictionary.
                # We handle them here to acknowledge them and avoid future confusion.
                pass

        return data

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
        if isinstance(condition, IsBlank):
            value = data.get(condition.question)
            return value is None or value == ""
        if isinstance(condition, GreaterThan):
            record_val_str = data.get(condition.question)
            if record_val_str is None or record_val_str == "":
                return False

            record_val = self._attempt_conversion(record_val_str)
            condition_val = self._attempt_conversion(condition.value)

            if (
                isinstance(record_val, str)
                or isinstance(condition_val, str)
                or type(record_val) is not type(condition_val)
            ):
                return False

            return record_val > condition_val
        if isinstance(condition, LessThan):
            record_val_str = data.get(condition.question)
            if record_val_str is None or record_val_str == "":
                return False

            record_val = self._attempt_conversion(record_val_str)
            condition_val = self._attempt_conversion(condition.value)

            if (
                isinstance(record_val, str)
                or isinstance(condition_val, str)
                or type(record_val) is not type(condition_val)
            ):
                return False

            return record_val < condition_val

        raise TypeError(f"Unknown condition type: {type(condition)}")
