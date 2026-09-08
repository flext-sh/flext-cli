"""Generic TOML helpers shared through ``u.Cli.toml_*``."""

from __future__ import annotations

from ._toml_parts.flextcliutilitiestoml_part_01 import (
    FlextCliUtilitiesToml as FlextCliUtilitiesTomlPart01,
)
from ._toml_parts.flextcliutilitiestoml_part_02 import (
    FlextCliUtilitiesToml as FlextCliUtilitiesTomlPart02,
)
from ._toml_parts.flextcliutilitiestoml_part_03 import (
    FlextCliUtilitiesToml as FlextCliUtilitiesTomlPart03,
)
from ._toml_parts.flextcliutilitiestoml_part_04 import (
    FlextCliUtilitiesToml as FlextCliUtilitiesTomlPart04,
)
from ._toml_parts.flextcliutilitiestoml_part_05 import (
    FlextCliUtilitiesToml as FlextCliUtilitiesTomlPart05,
)
from ._toml_parts.flextcliutilitiestoml_part_06 import (
    FlextCliUtilitiesToml as FlextCliUtilitiesTomlPart06,
)
from ._toml_parts.flextcliutilitiestoml_part_07 import (
    FlextCliUtilitiesToml as FlextCliUtilitiesTomlPart07,
)


class FlextCliUtilitiesToml(
    FlextCliUtilitiesTomlPart01,
    FlextCliUtilitiesTomlPart02,
    FlextCliUtilitiesTomlPart03,
    FlextCliUtilitiesTomlPart04,
    FlextCliUtilitiesTomlPart05,
    FlextCliUtilitiesTomlPart06,
    FlextCliUtilitiesTomlPart07,
):
    """Public facade for FlextCliUtilitiesToml."""


__all__: list[str] = ["FlextCliUtilitiesToml"]
