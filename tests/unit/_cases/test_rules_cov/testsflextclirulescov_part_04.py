"""Coverage tests for flext_cli._utilities.rules and services.rules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.constants import c
from tests.utilities import u

if TYPE_CHECKING:
    from tests.typings import t


class TestsFlextCliRulesCov:
    """Implementation part for TestsFlextCliRulesCov."""

    def test_rules_validate_matcher_valid(self) -> None:
        matcher = c.Tests.RULES_BASIC_MATCHER
        rule_def: t.JsonMapping = {"id": "rule-a", "actions": ["check"]}
        result = u.Cli.rules_validate_matcher(rule_def, matcher, rule_id_key="id")
        assert result is None

    def test_rules_validate_matcher_invalid_mapping(self) -> None:
        matcher = c.Tests.RULES_MAPPING_MATCHER
        rule_def: t.JsonMapping = {"id": "rule-a", "config": "not-a-mapping"}
        result = u.Cli.rules_validate_matcher(rule_def, matcher, rule_id_key="id")
        assert result is not None
        assert "config" in result

    def test_rules_validate_matcher_invalid_list(self) -> None:
        matcher = c.Tests.RULES_LIST_MATCHER
        rule_def: t.JsonMapping = {"id": "rule-a", "actions": []}
        result = u.Cli.rules_validate_matcher(rule_def, matcher, rule_id_key="id")
        assert result is not None
        assert "actions" in result


__all__: list[str] = ["TestsFlextCliRulesCov"]
