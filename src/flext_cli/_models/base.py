"""CLI Pydantic domain models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._models import FlextCliModelsBasePart01
from flext_cli._models import FlextCliModelsBasePart02
from flext_cli._models import FlextCliModelsBasePart03
from flext_cli._models import FlextCliModelsBasePart04
from flext_cli._models import FlextCliModelsBasePart05
from flext_cli._models import FlextCliModelsBasePart06
from flext_cli._models import FlextCliModelsBasePart07
from flext_cli._models import FlextCliModelsBasePart08
from flext_cli._models import FlextCliModelsBasePart09
from flext_cli._models import FlextCliModelsBasePart10
from flext_cli._models import FlextCliModelsAtomicSymlink


class FlextCliModelsBase(
    FlextCliModelsAtomicSymlink,
    FlextCliModelsBasePart01,
    FlextCliModelsBasePart02,
    FlextCliModelsBasePart03,
    FlextCliModelsBasePart04,
    FlextCliModelsBasePart05,
    FlextCliModelsBasePart06,
    FlextCliModelsBasePart07,
    FlextCliModelsBasePart08,
    FlextCliModelsBasePart09,
    FlextCliModelsBasePart10,
):
    """Public facade for FlextCliModelsBase."""


__all__: list[str] = ["FlextCliModelsBase"]
