"""FLEXT CLI Constants - Command-line interface configuration constants.

This module provides CLI-specific constants following flext-core patterns and extending
the semantic constant system. Constants are organized by functional domain to support
consistent CLI behavior across the FLEXT ecosystem.

Constant Categories:
    - Commands: Command types, names, and execution configuration
    - Validation: Input validation limits and pattern rules
    - Output: Display formatting and rendering configuration
    - Config: Configuration management and profile defaults
    - Timing: Timeout and duration constants for operations
    - Interface: UI elements, prompts, and user interaction constants

Integration:
    - Extends flext-core constants for ecosystem consistency
    - Used by domain entities for validation and business rules
    - Referenced by CLI command implementations for behavior
    - Supports configuration management and user preferences

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar

from flext_core.constants import FlextSemanticConstants

# =============================================================================
# CLI-SPECIFIC SEMANTIC CONSTANTS - Modern Python 3.13 Structure
# =============================================================================


class FlextCliSemanticConstants(FlextSemanticConstants):
    """CLI-specific semantic constants extending FlextSemanticConstants.

    Modern Python 3.13 constants following semantic grouping patterns.
    Extends the FLEXT ecosystem constants with command-line interface
    specific values while maintaining full backward compatibility.
    """

    class Commands:
        """Command type and execution constants."""

        # Command types
        SYSTEM = "system"
        PIPELINE = "pipeline"
        PLUGIN = "plugin"
        DATA = "data"
        CONFIG = "config"
        AUTH = "auth"
        MONITORING = "monitoring"

        # Command execution
        DEFAULT_TIMEOUT = 30
        MAX_COMMAND_HISTORY = 1000
        DEFAULT_RETRY_COUNT = 3

    class Validation:
        """Input validation limits and patterns."""

        MAX_ENTITY_NAME_LENGTH = 255
        MAX_ERROR_MESSAGE_LENGTH = 1000
        MAX_COMMAND_LINE_LENGTH = 8192
        MIN_ENTITY_NAME_LENGTH = 1

        # Username and identifier patterns
        USERNAME_PATTERN = r"^[a-zA-Z0-9_]{3,50}$"
        PROFILE_NAME_PATTERN = r"^[a-zA-Z0-9_-]{1,100}$"

    class Output:
        """Output formatting and display constants."""

        DEFAULT_OUTPUT_FORMAT = "table"
        SUPPORTED_FORMATS: ClassVar[list[str]] = ["table", "json", "yaml", "csv", "plain"]

        # Console output limits
        MAX_TABLE_ROWS = 1000
        DEFAULT_PAGE_SIZE = 20
        TRUNCATE_LENGTH = 100

    class Config:
        """Configuration management constants."""

        DEFAULT_PROFILE = "default"
        DEFAULT_CONFIG_FILE = "config.yaml"
        CONFIG_DIR = ".flx"

        # Environment variables
        PROFILE_ENV_VAR = "FLX_PROFILE"
        DEBUG_ENV_VAR = "FLX_DEBUG"
        CONFIG_PATH_ENV_VAR = "FLEXT_CLI_CONFIG_PATH"

    class Timing:
        """Timing and duration constants."""

        DEFAULT_SPINNER_DELAY = 0.1
        LONG_OPERATION_THRESHOLD = 5.0
        DEFAULT_POLL_INTERVAL = 1.0
        MAX_WAIT_TIME = 300

    class Interface:
        """User interface constants."""

        DEFAULT_CONSOLE_WIDTH = 120
        MIN_CONSOLE_WIDTH = 80

        # Rich styling
        SUCCESS_COLOR = "green"
        ERROR_COLOR = "red"
        WARNING_COLOR = "yellow"
        INFO_COLOR = "blue"

        # Prompts and messages
        CONFIRM_PROMPT = "Continue?"
        ABORT_MESSAGE = "Operation aborted by user"


class FlextCliConstants(FlextCliSemanticConstants):
    """CLI constants with backward compatibility.

    Legacy compatibility layer providing both modern semantic access
    and traditional flat constant access patterns for smooth migration.
    """

    # Modern semantic access (Primary API) - direct references
    Commands = FlextCliSemanticConstants.Commands
    Validation = FlextCliSemanticConstants.Validation
    Output = FlextCliSemanticConstants.Output
    Config = FlextCliSemanticConstants.Config
    Timing = FlextCliSemanticConstants.Timing
    Interface = FlextCliSemanticConstants.Interface

    # Legacy compatibility - flat access patterns (DEPRECATED - use semantic access)
    SYSTEM = FlextCliSemanticConstants.Commands.SYSTEM
    PIPELINE = FlextCliSemanticConstants.Commands.PIPELINE
    PLUGIN = FlextCliSemanticConstants.Commands.PLUGIN
    DATA = FlextCliSemanticConstants.Commands.DATA
    CONFIG = FlextCliSemanticConstants.Commands.CONFIG
    AUTH = FlextCliSemanticConstants.Commands.AUTH
    MONITORING = FlextCliSemanticConstants.Commands.MONITORING

    DEFAULT_TIMEOUT = FlextCliSemanticConstants.Commands.DEFAULT_TIMEOUT
    MAX_COMMAND_HISTORY = FlextCliSemanticConstants.Commands.MAX_COMMAND_HISTORY
    DEFAULT_RETRY_COUNT = FlextCliSemanticConstants.Commands.DEFAULT_RETRY_COUNT

    MAX_ENTITY_NAME_LENGTH = FlextCliSemanticConstants.Validation.MAX_ENTITY_NAME_LENGTH
    MAX_ERROR_MESSAGE_LENGTH = FlextCliSemanticConstants.Validation.MAX_ERROR_MESSAGE_LENGTH
    MAX_COMMAND_LINE_LENGTH = FlextCliSemanticConstants.Validation.MAX_COMMAND_LINE_LENGTH
    MIN_ENTITY_NAME_LENGTH = FlextCliSemanticConstants.Validation.MIN_ENTITY_NAME_LENGTH
    USERNAME_PATTERN = FlextCliSemanticConstants.Validation.USERNAME_PATTERN
    PROFILE_NAME_PATTERN = FlextCliSemanticConstants.Validation.PROFILE_NAME_PATTERN

    DEFAULT_OUTPUT_FORMAT = FlextCliSemanticConstants.Output.DEFAULT_OUTPUT_FORMAT
    SUPPORTED_FORMATS = FlextCliSemanticConstants.Output.SUPPORTED_FORMATS
    MAX_TABLE_ROWS = FlextCliSemanticConstants.Output.MAX_TABLE_ROWS
    DEFAULT_PAGE_SIZE = FlextCliSemanticConstants.Output.DEFAULT_PAGE_SIZE
    TRUNCATE_LENGTH = FlextCliSemanticConstants.Output.TRUNCATE_LENGTH

    DEFAULT_PROFILE = FlextCliSemanticConstants.Config.DEFAULT_PROFILE
    DEFAULT_CONFIG_FILE = FlextCliSemanticConstants.Config.DEFAULT_CONFIG_FILE
    CONFIG_DIR = FlextCliSemanticConstants.Config.CONFIG_DIR
    PROFILE_ENV_VAR = FlextCliSemanticConstants.Config.PROFILE_ENV_VAR
    DEBUG_ENV_VAR = FlextCliSemanticConstants.Config.DEBUG_ENV_VAR
    CONFIG_PATH_ENV_VAR = FlextCliSemanticConstants.Config.CONFIG_PATH_ENV_VAR


# Legacy alias for existing code compatibility (DEPRECATED)
CLIConstants = FlextCliConstants

# =============================================================================
# EXPORTS - CLI-specific constants API
# =============================================================================

__all__: list[str] = [
    "CLIConstants",
    "FlextCliConstants",
    "FlextCliSemanticConstants",
]

