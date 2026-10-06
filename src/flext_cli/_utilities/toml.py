"""Generic TOML helpers shared through ``u.Cli.toml_*``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._utilities._toml_parts.flextcliutilitiestoml_part_01 import (
    FlextCliUtilitiesTomlPart01,
)
from flext_cli._utilities._toml_parts.flextcliutilitiestoml_part_02 import (
    FlextCliUtilitiesTomlPart02,
)
from flext_cli._utilities._toml_parts.flextcliutilitiestoml_part_03 import (
    FlextCliUtilitiesTomlPart03,
)
from flext_cli._utilities._toml_parts.flextcliutilitiestoml_part_04 import (
    FlextCliUtilitiesTomlPart04,
)
from flext_cli._utilities._toml_parts.flextcliutilitiestoml_part_05 import (
    FlextCliUtilitiesTomlPart05,
)
from flext_cli._utilities._toml_parts.flextcliutilitiestoml_part_06 import (
    FlextCliUtilitiesTomlPart06,
)
from flext_cli._utilities._toml_parts.flextcliutilitiestoml_part_07 import (
    FlextCliUtilitiesTomlPart07,
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
