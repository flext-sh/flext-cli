"""CLI Pydantic domain models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._models._base.flextclimodelsbase_part_01 import FlextCliModelsBasePart01
from flext_cli._models._base.flextclimodelsbase_part_02 import FlextCliModelsBasePart02
from flext_cli._models._base.flextclimodelsbase_part_03 import FlextCliModelsBasePart03
from flext_cli._models._base.flextclimodelsbase_part_04 import FlextCliModelsBasePart04
from flext_cli._models._base.flextclimodelsbase_part_05 import FlextCliModelsBasePart05
from flext_cli._models._base.flextclimodelsbase_part_06 import FlextCliModelsBasePart06
from flext_cli._models._base.flextclimodelsbase_part_07 import FlextCliModelsBasePart07
from flext_cli._models._base.flextclimodelsbase_part_08 import FlextCliModelsBasePart08
from flext_cli._models._base.flextclimodelsbase_part_09 import FlextCliModelsBasePart09
from flext_cli._models._base.flextclimodelsbase_part_10 import FlextCliModelsBasePart10
from flext_cli._models.atomic_symlink import FlextCliModelsAtomicSymlink


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
