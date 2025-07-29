"""CLI domain models and services using flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

# Only import the entities that work
from flext_cli.domain.cli_services import CLIServiceContainer
from flext_cli.domain.entities import (
    CLICommand,
    CLIPlugin,
    CLISession,
    CommandStatus,
    CommandType,
)

__all__ = [
    "CLICommand",
    "CLIPlugin",
    "CLIServiceContainer",
    "CLISession",
    "CommandStatus",
    "CommandType",
]
