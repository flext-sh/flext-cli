"""Generic filesystem helpers shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._utilities import FlextCliUtilitiesFilesPart01
from flext_cli._utilities import FlextCliUtilitiesFilesPart02
from flext_cli._utilities import FlextCliUtilitiesFilesPart03
from flext_cli._utilities import FlextCliUtilitiesFilesPart04
from flext_cli._utilities import FlextCliUtilitiesFilesPart05
from flext_cli._utilities import FlextCliUtilitiesFilesPart06
from flext_cli._utilities import FlextCliUtilitiesSymlink


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
