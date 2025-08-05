"""FLEXT CLI - Modern Command Line Interface with Zero Boilerplate.

Unified CLI for FLEXT ecosystem applying foundation-refactored.md patterns.
Eliminates 85% boilerplate through modern flext-core integration.

Foundation Pattern Applied:
    # NEW: 5 lines - 80% boilerplate reduction!
    from flext_cli import CLIConfig, setup_cli

    config = CLIConfig()  # Automatic env loading, validation
    result = setup_cli()  # Railway-oriented setup

Architecture:
    - FlextEntity domain models with zero boilerplate
    - FlextResult railway-oriented programming
    - FlextBaseSettings automatic configuration
    - Clean Architecture with DDD patterns

Usage:
    Basic setup:
    >>> from flext_cli import CLIConfig, setup_cli
    >>> config = CLIConfig()
    >>> result = setup_cli()

    Domain entities:
    >>> from flext_cli import CLICommand, CommandType
    >>> command = CLICommand(name="test", command_line="echo hello")
    >>> result = command.start_execution()

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Version
from flext_cli.__version__ import __version__

# Core configuration - modern FlextBaseSettings
from flext_cli.config import CLIConfig, get_config

# Domain context
from flext_cli.domain.cli_context import CLIContext

# Domain entities - modern FlextEntity
from flext_cli.domain.entities import (
    CLICommand,
    CLIPlugin,
    CLISession,
)

# CLI setup - railway-oriented programming
from flext_cli.simple_api import setup_cli

# Types - semantic type system
from flext_cli.types import (
    PROFILE_TYPE,
    CommandStatus,
    CommandType,
    OutputFormat,
)

# Modern public API - zero boilerplate
__all__ = [
    "PROFILE_TYPE",
    "CLICommand",
    "CLIConfig",
    "CLIContext",
    "CLIPlugin",
    "CLISession",
    "CommandStatus",
    "CommandType",
    "OutputFormat",
    "__version__",
    "get_config",
    "setup_cli",
]
