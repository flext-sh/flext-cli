"""FlextCli Core - CLI building blocks using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Core components for zero-boilerplate CLI creation with massive code reduction.
"""

from __future__ import annotations

from .builder import FlextCliBuilder, FlextCliCommandConfig
from .data_exporter import FlextCliDataExporter
from .formatter import FlextCliFormatter
from .input import FlextCliInput
from .rich_gui import FlextCliRichGUI
from .validator import FlextCliValidator

__all__ = [
    "FlextCliBuilder",
    "FlextCliCommandConfig",
    "FlextCliDataExporter",
    "FlextCliFormatter",
    "FlextCliInput",
    "FlextCliRichGUI",
    "FlextCliValidator",
]
