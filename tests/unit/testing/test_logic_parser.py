from __future__ import annotations

import pytest

from imednet.testing.logic_parser import (
    And,
    BusinessRule,
    Checked,
    DisableAndClearField,
    Equals,
    LogicParser,
    Not,
    TrueCondition,
)


def test_parse_simple_disable_rule() -> None:
    """Test parsing a simple rule with a 'true' condition."""
    xml = """
    <BusinessLogic>
        <Conditions>
            <true/>
        </Conditions>
        <Actions>
            <disable_field>
                <question>AENUM</question>
            </disable_field>
        </Actions>
    </BusinessLogic>
    """
    parser = LogicParser()
    rule = parser.parse(xml)
    assert isinstance(rule, BusinessRule)
    assert isinstance(rule.conditions, TrueCondition)
    assert len(rule.actions) == 1
    assert rule.actions[0].question == "AENUM"


def test_parse_disable_and_clear_rule() -> None:
    """Test parsing a rule with a 'checked' condition and 'disable_and_clear' action."""
    xml = """
    <BusinessLogic>
        <Conditions>
            <and>
                <checked>
                    <question>IRBDATCB</question>
                </checked>
            </and>
        </Conditions>
        <Actions>
            <disable_and_clear_field>
                <question>IRBDAT</question>
            </disable_and_clear_field>
        </Actions>
    </BusinessLogic>
    """
    parser = LogicParser()
    rule = parser.parse(xml)
    assert isinstance(rule.conditions, And)
    assert isinstance(rule.conditions.conditions[0], Checked)
    assert rule.conditions.conditions[0].question == "IRBDATCB"
    assert isinstance(rule.actions[0], DisableAndClearField)
    assert rule.actions[0].question == "IRBDAT"


def test_parse_not_equals_rule() -> None:
    """Test parsing a rule with a 'not equals' condition."""
    xml = """
    <BusinessLogic>
        <Conditions>
            <and>
                <not>
                    <equals>
                        <question>SAEYN</question>
                        <value>Yes</value>
                    </equals>
                </not>
            </and>
        </Conditions>
        <Actions>
            <disable_and_clear_field>
                <question>UADEYN</question>
            </disable_and_clear_field>
        </Actions>
    </BusinessLogic>
    """
    parser = LogicParser()
    rule = parser.parse(xml)
    assert isinstance(rule.conditions.conditions[0], Not)
    not_condition = rule.conditions.conditions[0]
    assert isinstance(not_condition.condition, Equals)
    assert not_condition.condition.question == "SAEYN"
    assert not_condition.condition.value == "Yes"
