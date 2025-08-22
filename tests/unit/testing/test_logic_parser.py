from __future__ import annotations

from imednet.testing.logic_parser import (
    And,
    BusinessRule,
    Checked,
    DisableAndClearField,
    DisableField,
    Equals,
    GreaterThan,
    IsBlank,
    LessThan,
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
    action = rule.actions[0]
    assert isinstance(action, DisableField)
    assert action.question == "AENUM"


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
    condition = rule.conditions.conditions[0]
    assert isinstance(condition, Checked)
    assert condition.question == "IRBDATCB"
    action = rule.actions[0]
    assert isinstance(action, DisableAndClearField)
    assert action.question == "IRBDAT"


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
    assert isinstance(rule.conditions, And)
    not_condition_outer = rule.conditions.conditions[0]
    assert isinstance(not_condition_outer, Not)
    assert isinstance(not_condition_outer.condition, Equals)
    assert not_condition_outer.condition.question == "SAEYN"
    assert not_condition_outer.condition.value == "Yes"


def test_parse_greater_than_rule() -> None:
    """Test parsing a rule with a 'greater than' condition."""
    xml = """
    <BusinessLogic>
        <Conditions>
            <gt>
                <question>AGE</question>
                <value>18</value>
            </gt>
        </Conditions>
        <Actions>
            <disable_and_clear_field>
                <question>ADULT_ONLY</question>
            </disable_and_clear_field>
        </Actions>
    </BusinessLogic>
    """
    parser = LogicParser()
    rule = parser.parse(xml)
    assert isinstance(rule.conditions, GreaterThan)
    assert rule.conditions.question == "AGE"
    assert rule.conditions.value == "18"


def test_parse_less_than_rule() -> None:
    """Test parsing a rule with a 'less than' condition."""
    xml = """
    <BusinessLogic>
        <Conditions>
            <lt>
                <question>VISIT_DATE</question>
                <value>01-JAN-2025</value>
            </lt>
        </Conditions>
        <Actions>
            <disable_and_clear_field>
                <question>FUTURE_VISIT</question>
            </disable_and_clear_field>
        </Actions>
    </BusinessLogic>
    """
    parser = LogicParser()
    rule = parser.parse(xml)
    assert isinstance(rule.conditions, LessThan)
    assert rule.conditions.question == "VISIT_DATE"
    assert rule.conditions.value == "01-JAN-2025"


def test_parse_is_blank_rule() -> None:
    """Test parsing a rule with an 'is blank' condition."""
    xml = """
    <BusinessLogic>
        <Conditions>
            <blank>
                <question>DEATH_DATE</question>
            </blank>
        </Conditions>
        <Actions>
            <disable_and_clear_field>
                <question>ALIVE_FIELD</question>
            </disable_and_clear_field>
        </Actions>
    </BusinessLogic>
    """
    parser = LogicParser()
    rule = parser.parse(xml)
    assert isinstance(rule.conditions, IsBlank)
    assert rule.conditions.question == "DEATH_DATE"
