"""FlextCli protocol definitions - Structural typing contracts.

The generated model-protocol holders mirror the m.Cli models; composing them
here publishes each projected contract on p.Cli beside the authored ones.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._protocols import (
    FlextCliProtocolsAtomicPublication,
    FlextCliProtocolsAtomicSymlink,
)
from flext_cli._protocols._base import (
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
    FlextCliProtocolsBasePart05,
)


class FlextCliProtocolsBase(
    FlextCliProtocolsAtomicPublication,
    FlextCliProtocolsAtomicSymlink,
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
    FlextCliProtocolsBasePart05,
):
    """Public facade for FlextCliProtocolsBase."""


__all__: list[str] = ["FlextCliProtocolsBase"]
