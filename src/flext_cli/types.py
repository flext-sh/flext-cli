"""FLEXT CLI Types - Modern Type System with Zero Boilerplate.

Semantic type definitions following foundation-refactored.md patterns.
Eliminates 85% type duplication through flext-core integration.

Foundation Pattern Applied:
    # NEW: Clear, hierarchical type system
    from flext_core.types import FlextTypes

    # Self-documenting types
    user_predicate: FlextTypes.Core.Predicate[User] = lambda u: u.is_active

Architecture:
    - flext-core type system integration
    - Click parameter types for CLI validation
    - Zero boilerplate enum definitions
    - Semantic clarity through domain types

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

import click
from flext_core.types import FlextTypes

# Type aliases for legacy compatibility
from flext_cli.config import CLIConfig
from flext_cli.domain.cli_context import CLIContext
from flext_cli.domain.entities import CLICommand, CLIPlugin, CLISession

# CLI semantic types - leveraging flext-core
OutputFormat = Literal["table", "json", "yaml", "csv", "plain"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]
ProfileName = str
CommandName = str

# flext-core type integration
CLIValidator = FlextTypes.Core.Validator[object]
CLIPredicate = FlextTypes.Core.Predicate[object]


class CommandStatus(StrEnum):
    """Command execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CommandType(StrEnum):
    """Command categories."""

    CLI = "cli"
    SYSTEM = "system"
    SCRIPT = "script"
    SQL = "sql"
    PIPELINE = "pipeline"
    PLUGIN = "plugin"
    DATA = "data"
    CONFIG = "config"
    AUTH = "auth"
    MONITORING = "monitoring"


# Click parameter types
class ProfileType(click.ParamType):
    """Profile parameter type."""

    name = "profile"

    def convert(
        self, value: object, param: click.Parameter | None, ctx: click.Context | None,
    ) -> str:
        """Convert value to profile string."""
        if isinstance(value, str):
            return value
        self.fail(f"{value!r} is not a valid profile", param, ctx)
        return ""  # type: ignore[unreachable]  # Click pattern requirement


# Singleton instances
PROFILE_TYPE = ProfileType()

FlextCliConfig = CLIConfig
FlextCliContext = CLIContext
FlextCliCommand = CLICommand
FlextCliPlugin = CLIPlugin
FlextCliSession = CLISession
FlextCliCommandStatus = CommandStatus
FlextCliCommandType = CommandType
FlextCliOutputFormat = OutputFormat

# Legacy type aliases
TCliData = object
TCliFormat = OutputFormat
TCliPath = str
TCliArgs = dict[str, object]
TCliConfig = CLIConfig
TCliHandler = object  # Generic handler type
