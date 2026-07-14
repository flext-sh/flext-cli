"""FlextCli protocol definitions - Structural typing contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_cli._protocols._base_parts.flextcliprotocolsbase_part_04 import (
    FlextCliProtocolsBase as FlextCliProtocolsBasePart04,
)

# mro-wkii.17.26 (codex): YAML protocol data is defined by the upstream JSON
# alias; importing the local t facade would re-enter its own p composition.
from flext_core import t


class FlextCliProtocolsBase(FlextCliProtocolsBasePart04):
    """Implementation part for FlextCliProtocolsBase."""

    @runtime_checkable
    class YamlModule(Protocol):
        """Protocol for YAML serialization module interface."""

        def dump(self, data: t.JsonPayload, *, default_flow_style: bool = True) -> str:
            """Dump data as YAML string."""
            ...


__all__: tuple[str, ...] = ("FlextCliProtocolsBase",)
