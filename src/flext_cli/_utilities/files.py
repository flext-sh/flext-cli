"""Generic filesystem helpers shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_01 import (
    FlextCliUtilitiesFilesPart01,
)
from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_02 import (
    FlextCliUtilitiesFilesPart02,
)
from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_03 import (
    FlextCliUtilitiesFilesPart03,
)
from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_04 import (
    FlextCliUtilitiesFilesPart04,
)
from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_05 import (
    FlextCliUtilitiesFilesPart05,
)
from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_06 import (
    FlextCliUtilitiesFilesPart06,
)
from flext_cli._utilities.symlink import FlextCliUtilitiesSymlink


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
