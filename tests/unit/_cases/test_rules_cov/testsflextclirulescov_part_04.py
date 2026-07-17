"""Coverage tests for flext_cli._utilities.rules and services.rules."""

from __future__ import annotations


from tests import c
from tests import u
from flext_tests import tm

from tests import t


class TestsFlextCliRulesCov:
    """Implementation part for TestsFlextCliRulesCov."""

    def test_rules_validate_matcher_valid(self) -> None:
        """Verify that rules validate matcher valid."""
        matcher = c.Tests.RULES_BASIC_MATCHER
        rule_def: t.JsonMapping = {"id": "rule-a", "actions": ["check"]}
        result = u.Cli.rules_validate_matcher(rule_def, matcher, rule_id_key="id")
        tm.that(result, none=True)

    def test_rules_validate_matcher_invalid_mapping(self) -> None:
        """Verify that rules validate matcher invalid mapping."""
        matcher = c.Tests.RULES_MAPPING_MATCHER
        rule_def: t.JsonMapping = {"id": "rule-a", "config": "not-a-mapping"}
        result = u.Cli.rules_validate_matcher(rule_def, matcher, rule_id_key="id")
        result = tm.not_none(result)
        tm.that(result, has="config")

    def test_rules_validate_matcher_invalid_list(self) -> None:
        """Verify that rules validate matcher invalid list."""
        matcher = c.Tests.RULES_LIST_MATCHER
        rule_def: t.JsonMapping = {"id": "rule-a", "actions": []}
        result = u.Cli.rules_validate_matcher(rule_def, matcher, rule_id_key="id")
        result = tm.not_none(result)
        tm.that(result, has="actions")


__all__: list[str] = ["TestsFlextCliRulesCov"]
