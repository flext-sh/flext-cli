"""FlextCli protocol definitions - Structural typing contracts.

The generated model-protocol holders mirror the m.Cli models; composing them
here publishes each projected contract on p.Cli beside the authored ones.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._protocols._base import FlextCliProtocolsBasePart05
from flext_cli._protocols._base.flextclimodelsbase_part_01 import (
    FlextCliProtocolsBaseFlextclimodelsbasePart01,
)
from flext_cli._protocols._base.flextclimodelsbase_part_02 import (
    FlextCliProtocolsBaseFlextclimodelsbasePart02,
)
from flext_cli._protocols._base.flextclimodelsbase_part_03 import (
    FlextCliProtocolsBaseFlextclimodelsbasePart03,
)
from flext_cli._protocols._base.flextclimodelsbase_part_04 import (
    FlextCliProtocolsBaseFlextclimodelsbasePart04,
)
from flext_cli._protocols._base.flextclimodelsbase_part_05 import (
    FlextCliProtocolsBaseFlextclimodelsbasePart05,
)
from flext_cli._protocols._base.flextclimodelsbase_part_06 import (
    FlextCliProtocolsBaseFlextclimodelsbasePart06,
)
from flext_cli._protocols._base.flextclimodelsbase_part_07 import (
    FlextCliProtocolsBaseFlextclimodelsbasePart07,
)
from flext_cli._protocols._base.flextclimodelsbase_part_08 import (
    FlextCliProtocolsBaseFlextclimodelsbasePart08,
)
from flext_cli._protocols._base.flextclimodelsbase_part_09 import (
    FlextCliProtocolsBaseFlextclimodelsbasePart09,
)
from flext_cli._protocols._base.flextclimodelsbase_part_10 import (
    FlextCliProtocolsBaseFlextclimodelsbasePart10,
)


class FlextCliProtocolsBase(
    FlextCliProtocolsBasePart05,
    FlextCliProtocolsBaseFlextclimodelsbasePart01,
    FlextCliProtocolsBaseFlextclimodelsbasePart02,
    FlextCliProtocolsBaseFlextclimodelsbasePart03,
    FlextCliProtocolsBaseFlextclimodelsbasePart04,
    FlextCliProtocolsBaseFlextclimodelsbasePart05,
    FlextCliProtocolsBaseFlextclimodelsbasePart06,
    FlextCliProtocolsBaseFlextclimodelsbasePart07,
    FlextCliProtocolsBaseFlextclimodelsbasePart08,
    FlextCliProtocolsBaseFlextclimodelsbasePart09,
    FlextCliProtocolsBaseFlextclimodelsbasePart10,
):
    """Public facade for FlextCliProtocolsBase."""


__all__: list[str] = ["FlextCliProtocolsBase"]
