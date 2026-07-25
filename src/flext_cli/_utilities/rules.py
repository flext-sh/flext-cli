"""Generic local-rule loading helpers shared through ``u.Cli.rules_*``."""

from __future__ import annotations

from flext_cli._utilities._rules_parts.flextcliutilitiesrules_part_01 import (
    FlextCliUtilitiesRules as FlextCliUtilitiesRulesPart01,
)
from flext_cli._utilities._rules_parts.flextcliutilitiesrules_part_02 import (
    FlextCliUtilitiesRules as FlextCliUtilitiesRulesPart02,
)
from flext_cli._utilities._rules_parts.flextcliutilitiesrules_part_03 import (
    FlextCliUtilitiesRules as FlextCliUtilitiesRulesPart03,
)


class FlextCliUtilitiesRules(
    FlextCliUtilitiesRulesPart01,
    FlextCliUtilitiesRulesPart02,
    FlextCliUtilitiesRulesPart03,
):
    """Public facade for FlextCliUtilitiesRules."""


__all__: list[str] = ["FlextCliUtilitiesRules"]
