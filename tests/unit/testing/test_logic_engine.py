from __future__ import annotations

from imednet.testing.logic_engine import LogicEngine
from imednet.testing.logic_parser import (
    And,
    BusinessRule,
    Checked,
    DisableAndClearField,
    Equals,
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
    assert actions[0].question == "A"


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
