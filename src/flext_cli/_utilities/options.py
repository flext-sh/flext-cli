"""CLI option helpers shared through ``u.Cli``."""

from __future__ import annotations

from flext_cli._utilities._options_parts.flextcliutilitiesoptionbuilder_part_01 import (
    FlextCliUtilitiesOptionBuilder as FlextCliUtilitiesOptionBuilderPart01,
)
from flext_cli._utilities._options_parts.flextcliutilitiesoptions_part_02 import (
    FlextCliUtilitiesOptions as FlextCliUtilitiesOptionsPart02,
)


class FlextCliUtilitiesOptionBuilder(
    FlextCliUtilitiesOptionBuilderPart01,
):
    """Public facade for FlextCliUtilitiesOptionBuilder."""


class FlextCliUtilitiesOptions(FlextCliUtilitiesOptionsPart02):
    """Public facade for FlextCliUtilitiesOptions."""


__all__: list[str] = ["FlextCliUtilitiesOptionBuilder", "FlextCliUtilitiesOptions"]
