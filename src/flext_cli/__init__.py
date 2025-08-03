"""FLEXT CLI - Unified Command Line Interface for FLEXT Ecosystem.

This module provides the primary API for FLEXT CLI, a comprehensive command-line
interface that serves as the operational gateway for the entire FLEXT distributed
data integration ecosystem (32+ projects).

Key Features:
    - Domain-driven design with rich CLI entities (CLICommand, CLISession, CLIPlugin)
    - Railway-oriented programming with FlextResult error handling
    - Click-based command framework with Rich terminal UI
    - Ecosystem integration with FlexCore and FLEXT services
    - CQRS patterns for enterprise-grade command handling

Architecture:
    Following Clean Architecture with flext-core integration:
    - Presentation Layer: Click commands with Rich output
    - Application Layer: CQRS command handlers
    - Domain Layer: Business entities and services
    - Infrastructure Layer: Service clients and DI container

Usage:
    Basic CLI setup:
    >>> from flext_cli import setup_cli, CLISettings
    >>> settings = CLISettings(debug=True)
    >>> result = setup_cli(settings)
    >>> if result.is_success:
    ...     print("CLI ready")

    Domain entity usage:
    >>> from flext_cli import CLICommand, CommandType
    >>> command = CLICommand(
    ...     name="test-command",
    ...     command_line="echo hello",
    ...     command_type=CommandType.SYSTEM
    ... )
    >>> result = command.start_execution()

Current Implementation Status:
    ✅ 30% Complete: Core foundation, auth/config/debug commands
    📋 70% Pending: Pipeline, service, data, plugin, monitoring commands

    See docs/TODO.md for detailed implementation roadmap.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Version from centralized version management
from flext_cli.__version__ import __version__

# Convenience functions for library use
from flext_cli.api import (
    flext_cli_aggregate_data,
    flext_cli_batch_export,
    flext_cli_export,
    flext_cli_format,
    flext_cli_table,
    flext_cli_transform_data,
    flext_cli_unwrap_or_default,
    flext_cli_unwrap_or_none,
)

# Core utilities for CLI development
from flext_cli.core.base import (
    CLIContext,
    handle_service_result,
)

# Core decorators and helpers
from flext_cli.core.decorators import (
    async_command,
    confirm_action,
    measure_time,
    require_auth,
    retry,
    validate_config,
    with_spinner,
)

# Core formatters
from flext_cli.core.formatters import (
    FormatterFactory,
    format_output,
)
from flext_cli.core.helpers import CLIHelper
from flext_cli.core.types import (
    URL,
    ClickPath,
    ExistingDir,
    ExistingFile,
    NewFile,
    PositiveInt,
)

# Domain entities - core business objects
from flext_cli.domain.entities import (
    CLICommand,
    CLIPlugin,
    CLISession,
    CommandStatus,
    CommandType,
)

# Simple API for programmatic use
from flext_cli.simple_api import setup_cli

# Configuration and utilities
from flext_cli.utils.config import (
    CLIConfig,
    CLISettings,
    get_config,
    get_settings,
)

__all__ = [
    "URL",
    # Core Domain Entities
    "CLICommand",
    # Configuration
    "CLIConfig",
    "CLIContext",
    # Core Utilities
    "CLIHelper",
    "CLIPlugin",
    "CLISession",
    "CLISettings",
    # Types
    "ClickPath",
    "CommandStatus",
    "CommandType",
    "ExistingDir",
    "ExistingFile",
    "FormatterFactory",
    "NewFile",
    "PositiveInt",
    # Version
    "__version__",
    # Decorators
    "async_command",
    "confirm_action",
    # Convenience API functions
    "flext_cli_aggregate_data",
    "flext_cli_batch_export",
    "flext_cli_export",
    "flext_cli_format",
    "flext_cli_table",
    "flext_cli_transform_data",
    "flext_cli_unwrap_or_default",
    "flext_cli_unwrap_or_none",
    "format_output",
    "get_config",
    "get_settings",
    "handle_service_result",
    "measure_time",
    "require_auth",
    "retry",
    "setup_cli",
    "validate_config",
    "with_spinner",
]
