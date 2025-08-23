from __future__ import annotations

import pytest

from imednet.testing.logic_engine import LogicEngine
from imednet.testing.logic_parser import (
    And,
    BusinessRule,
    Checked,
    DisableAndClearField,
    Equals,
    GreaterThan,
    HideAndClearField,
    IsBlank,
    LessThan,
    Not,
    TrueCondition,
)


def test_engine_evaluates_true_condition() -> None:
    """Test that a rule with a 'true' condition is always evaluated."""
    rule = BusinessRule(
        conditions=TrueCondition(),
        actions=[DisableAndClearField(question="A")],
    )
    engine = LogicEngine(rules=[rule])
    actions = engine.evaluate(data={})
    assert len(actions) == 1
    action = actions[0]
    assert isinstance(action, DisableAndClearField)
    assert action.question == "A"


def test_engine_evaluates_checked_condition() -> None:
    """Test that a 'checked' condition is evaluated correctly."""
    rule = BusinessRule(
        conditions=Checked(question="B"),
        actions=[DisableAndClearField(question="A")],
    )
    engine = LogicEngine(rules=[rule])

    # Condition met
    actions = engine.evaluate(data={"B": "1"})
    assert len(actions) == 1

    # Condition not met
    actions = engine.evaluate(data={"B": "0"})
    assert len(actions) == 0

    # Question not in data
    actions = engine.evaluate(data={})
    assert len(actions) == 0


def test_engine_evaluates_not_equals_condition() -> None:
    """Test that a 'not equals' condition is evaluated correctly."""
    rule = BusinessRule(
        conditions=Not(Equals(question="B", value="Yes")),
        actions=[DisableAndClearField(question="A")],
    )
    engine = LogicEngine(rules=[rule])

    # Condition met (B is not "Yes")
    actions = engine.evaluate(data={"B": "No"})
    assert len(actions) == 1

    # Condition not met (B is "Yes")
    actions = engine.evaluate(data={"B": "Yes"})
    assert len(actions) == 0


def test_engine_evaluates_and_condition() -> None:
    """Test that an 'and' condition is evaluated correctly."""
    rule = BusinessRule(
        conditions=And(
            conditions=[
                Checked(question="B"),
                Equals(question="C", value="Value"),
            ]
        ),
        actions=[DisableAndClearField(question="A")],
    )
    engine = LogicEngine(rules=[rule])

    # Both conditions met
    actions = engine.evaluate(data={"B": "1", "C": "Value"})
    assert len(actions) == 1

    # First condition not met
    actions = engine.evaluate(data={"B": "0", "C": "Value"})
    assert len(actions) == 0

    # Second condition not met
    actions = engine.evaluate(data={"B": "1", "C": "Other"})
    assert len(actions) == 0


@pytest.mark.parametrize(
    "data, expected_actions",
    [
        ({"A": ""}, 1),
        ({"A": None}, 1),
        ({}, 1),
        ({"A": "has value"}, 0),
    ],
)
def test_engine_evaluates_is_blank(data, expected_actions) -> None:
    """Test that an 'is blank' condition is evaluated correctly."""
    rule = BusinessRule(
        conditions=IsBlank(question="A"),
        actions=[DisableAndClearField(question="B")],
    )
    engine = LogicEngine(rules=[rule])
    actions = engine.evaluate(data=data)
    assert len(actions) == expected_actions


@pytest.mark.parametrize(
    "data, value, expected_actions",
    [
        # Numeric comparisons
        ({"A": "10"}, "5", 1),
        ({"A": "5"}, "5", 0),
        ({"A": "4"}, "5", 0),
        ({"A": "10.5"}, "10.4", 1),
        # Date comparisons
        ({"A": "02-JAN-2024"}, "01-JAN-2024", 1),
        ({"A": "01-JAN-2024"}, "01-JAN-2024", 0),
        ({"A": "01-JAN-2024"}, "02-JAN-2024", 0),
        # Type mismatch
        ({"A": "10"}, "01-JAN-2024", 0),
        # Blank or missing data
        ({"A": ""}, "5", 0),
        ({}, "5", 0),
    ],
)
def test_engine_evaluates_greater_than(data, value, expected_actions) -> None:
    """Test that a 'greater than' condition is evaluated correctly."""
    rule = BusinessRule(
        conditions=GreaterThan(question="A", value=value),
        actions=[DisableAndClearField(question="B")],
    )
    engine = LogicEngine(rules=[rule])
    actions = engine.evaluate(data=data)
    assert len(actions) == expected_actions


@pytest.mark.parametrize(
    "data, value, expected_actions",
    [
        # Numeric comparisons
        ({"A": "5"}, "10", 1),
        ({"A": "5"}, "5", 0),
        ({"A": "6"}, "5", 0),
        ({"A": "10.4"}, "10.5", 1),
        # Date comparisons
        ({"A": "01-JAN-2024"}, "02-JAN-2024", 1),
        ({"A": "01-JAN-2024"}, "01-JAN-2024", 0),
        ({"A": "02-JAN-2024"}, "01-JAN-2024", 0),
        # Type mismatch
        ({"A": "10"}, "01-JAN-2024", 0),
        # Blank or missing data
        ({"A": ""}, "5", 0),
        ({}, "5", 0),
    ],
)
def test_engine_evaluates_less_than(data, value, expected_actions) -> None:
    """Test that a 'less than' condition is evaluated correctly."""
    rule = BusinessRule(
        conditions=LessThan(question="A", value=value),
        actions=[DisableAndClearField(question="B")],
    )
    engine = LogicEngine(rules=[rule])
    actions = engine.evaluate(data=data)
    assert len(actions) == expected_actions


def test_engine_executes_actions() -> None:
    """Test that the engine correctly executes actions that modify data."""
    rules = [
        BusinessRule(
            conditions=Checked(question="A"),
            actions=[DisableAndClearField(question="B")],
        ),
        BusinessRule(
            conditions=Equals(question="C", value="hide"),
            actions=[HideAndClearField(question="D")],
        ),
    ]
    engine = LogicEngine(rules=rules)

    # Initial data
    data = {"A": "1", "B": "some value", "C": "hide", "D": "another value"}

    # Execute the logic
    modified_data = engine.execute(data)

    # Check that the data was modified as expected
    assert modified_data["A"] == "1"
    assert modified_data["B"] == ""
    assert modified_data["C"] == "hide"
    assert modified_data["D"] == ""
