from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List


# --- Condition data classes ---
@dataclass
class Condition:
    """Base class for a condition."""


@dataclass
class And(Condition):
    """Represents a logical AND of multiple conditions."""
    conditions: List[Condition]


@dataclass
class Or(Condition):
    """Represents a logical OR of multiple conditions."""
    conditions: List[Condition]


@dataclass
class Not(Condition):
    """Represents a logical NOT of a single condition."""
    condition: Condition


@dataclass
class Equals(Condition):
    """Represents an equality condition."""
    question: str
    value: str


@dataclass
class Checked(Condition):
    """Represents a condition where a checkbox is checked."""
    question: str


@dataclass
class TrueCondition(Condition):
    """Represents a condition that is always true."""


@dataclass
class GreaterThan(Condition):
    """Represents a greater than condition."""
    question: str
    value: str


@dataclass
class LessThan(Condition):
    """Represents a less than condition."""
    question: str
    value: str


@dataclass
class IsBlank(Condition):
    """Represents a condition where a field is blank."""
    question: str


# --- Action data classes ---
@dataclass
class Action:
    """Base class for an action."""


@dataclass
class DisableField(Action):
    """Represents an action to disable a field."""
    question: str


@dataclass
class DisableAndClearField(Action):
    """Represents an action to disable and clear a field."""
    question: str


@dataclass
class HideField(Action):
    """Represents an action to hide a field."""
    question: str


@dataclass
class HideAndClearField(Action):
    """Represents an action to hide and clear a field."""
    question: str


@dataclass
class BusinessRule:
    """Represents a single business logic rule."""
    conditions: Condition
    actions: List[Action]


class LogicParser:
    """Parses business logic XML into structured objects."""

    def parse(self, xml_string: str) -> BusinessRule:
        """
        Parses an XML string containing business logic.

        Args:
            xml_string: The XML string to parse.

        Returns:
            A BusinessRule object representing the parsed logic.
        """
        root = ET.fromstring(xml_string)
        conditions_root = root.find("Conditions")
        actions_root = root.find("Actions")

        if conditions_root is None or actions_root is None:
            raise ValueError("Invalid business logic XML: Missing Conditions or Actions.")

        conditions = self._parse_condition(next(iter(conditions_root)))
        actions = [self._parse_action(action_el) for action_el in actions_root]

        return BusinessRule(conditions=conditions, actions=actions)

    def _parse_condition(self, element: ET.Element) -> Condition:
        """Recursively parses a condition element."""
        tag = element.tag
        if tag == "and":
            return And([self._parse_condition(child) for child in element])
        if tag == "or":
            return Or([self._parse_condition(child) for child in element])
        if tag == "not":
            return Not(self._parse_condition(next(iter(element))))

        def get_text(el_name: str) -> str:
            child_el = element.find(el_name)
            if child_el is None or child_el.text is None:
                raise ValueError(f"<{tag}> condition is missing a <{el_name}> tag.")
            return child_el.text

        if tag == "equals":
            return Equals(question=get_text("question"), value=get_text("value"))
        if tag == "gt":
            return GreaterThan(question=get_text("question"), value=get_text("value"))
        if tag == "lt":
            return LessThan(question=get_text("question"), value=get_text("value"))
        if tag == "blank":
            return IsBlank(question=get_text("question"))
        if tag == "checked":
            return Checked(question=get_text("question"))
        if tag == "true":
            return TrueCondition()

        raise ValueError(f"Unknown condition tag: {tag}")

    def _parse_action(self, element: ET.Element) -> Action:
        """Parses an action element."""
        tag = element.tag
        question_tag = element.find("question")

        if question_tag is None or question_tag.text is None:
            raise ValueError(f"Invalid <{tag}> action: missing question.")
        question = question_tag.text

        if tag == "disable_field":
            return DisableField(question=question)
        if tag == "disable_and_clear_field":
            return DisableAndClearField(question=question)
        if tag == "hide_field":
            return HideField(question=question)
        if tag == "hide_and_clear_field":
            return HideAndClearField(question=question)

        raise ValueError(f"Unknown action tag: {tag}")
