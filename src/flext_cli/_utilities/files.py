"""Generic filesystem helpers shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._utilities._files.binary_reads import FlextCliUtilitiesFilesPart03
from flext_cli._utilities._files.flextcliutilitiesfiles_part_05 import (
    FlextCliUtilitiesFilesPart05,
)
from flext_cli._utilities._files.flextcliutilitiesfiles_part_06 import (
    FlextCliUtilitiesFilesPart06,
)
from flext_cli._utilities._files.formats import FlextCliUtilitiesFilesPart04
from flext_cli._utilities._files.text_formats import FlextCliUtilitiesFilesPart01
from flext_cli._utilities._files.writes import FlextCliUtilitiesFilesPart02


class FlextCliUtilitiesFiles(
    FlextCliUtilitiesFilesPart01,
    FlextCliUtilitiesFilesPart02,
    FlextCliUtilitiesFilesPart03,
    FlextCliUtilitiesFilesPart04,
    FlextCliUtilitiesFilesPart05,
    FlextCliUtilitiesFilesPart06,
):
    """Public facade for FlextCliUtilitiesFiles."""


__all__: list[str] = ["FlextCliUtilitiesFiles"]
