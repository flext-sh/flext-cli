"""FLEXT CLI Library - Command Line Interface Development Toolkit.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

A powerful Python library for building command-line interfaces using
flext-core foundation.
Provides domain entities, utilities, and patterns for robust CLI development.
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
