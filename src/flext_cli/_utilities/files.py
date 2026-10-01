"""Generic filesystem helpers shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from ._files_parts.flextcliutilitiesfiles_part_01 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart01,
)
from ._files_parts.flextcliutilitiesfiles_part_02 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart02,
)
from ._files_parts.flextcliutilitiesfiles_part_03 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart03,
)
from ._files_parts.flextcliutilitiesfiles_part_04 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart04,
)
from ._files_parts.flextcliutilitiesfiles_part_05 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart05,
)
from ._files_parts.flextcliutilitiesfiles_part_06 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart06,
)
from .symlink import FlextCliUtilitiesSymlink


class FlextCliUtilitiesFiles(
    FlextCliUtilitiesSymlink,
    FlextCliUtilitiesFilesPart01,
    FlextCliUtilitiesFilesPart02,
    FlextCliUtilitiesFilesPart03,
    FlextCliUtilitiesFilesPart04,
    FlextCliUtilitiesFilesPart05,
    FlextCliUtilitiesFilesPart06,
):
    """Public facade for FlextCliUtilitiesFiles."""


__all__: list[str] = ["FlextCliUtilitiesFiles"]
