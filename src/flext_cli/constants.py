"""FLEXT CLI Constants - Centralized CLI-specific constants.

This module delegates to flext_core.constants.FlextConstants for all shared constants
and only defines CLI-specific constants that don't exist in core.

Follows SOLID principles:
- Single Responsibility: Only CLI-specific constants
- Don't Repeat Yourself: Delegates to flext-core
- Interface Segregation: Exposes only what's needed

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import warnings
from typing import ClassVar, Final

from flext_core import FlextConstants

# =============================================================================
# CLI-SPECIFIC CONSTANTS
# =============================================================================

# CLI-specific environment configuration
CLI_ENV_PREFIX: Final[str] = "FLEXT_CLI_"
CLI_PROFILE_ENV_VAR: Final[str] = "FLX_PROFILE"
CLI_DEBUG_ENV_VAR: Final[str] = "FLX_DEBUG"

# CLI-specific behavior defaults
DEFAULT_PROFILE: Final[str] = "default"
DEFAULT_CONFIRM_PROMPT: Final[str] = "Are you sure?"
DEFAULT_RICH_THEME: Final[str] = "monokai"

# CLI-specific output formats (extends core)
OUTPUT_FORMAT_RICH: Final[str] = "rich"
OUTPUT_FORMAT_PLAIN: Final[str] = "plain"

# CLI-specific validation (extends core limits)
MAX_COMMAND_LENGTH: Final[int] = 512
MAX_PROMPT_LENGTH: Final[int] = 256

# =============================================================================
# DELEGATE TO FLEXT-CORE CONSTANTS
# =============================================================================

# API defaults - delegate to flext-core Platform constants
DEFAULT_API_URL: str = f"{FlextConstants.Platform.DEFAULT_BASE_URL}:{FlextConstants.Platform.FLEXT_API_PORT}"
DEFAULT_TIMEOUT: int = FlextConstants.Defaults.TIMEOUT
DEFAULT_RETRIES: int = FlextConstants.Defaults.MAX_RETRIES

# Output defaults - delegate to flext-core
DEFAULT_OUTPUT_FORMAT: str = FlextConstants.Cli.DEFAULT_OUTPUT_FORMAT
DEFAULT_LOG_LEVEL: str = FlextConstants.Observability.DEFAULT_LOG_LEVEL

# CLI behavior - delegate to flext-core
DEFAULT_DEBUG: bool = False  # CLI-specific default

# Environment configuration - delegate to flext-core
ENV_PREFIX: str = CLI_ENV_PREFIX  # Use CLI-specific prefix
ENV_FILE: str = FlextConstants.Configuration.DOTENV_FILES[0]

# Validation limits - delegate to flext-core
MAX_TIMEOUT: int = FlextConstants.Limits.MAX_PORT  # Reuse appropriate limit
MIN_TIMEOUT: int = FlextConstants.Defaults.VALIDATION_TIMEOUT
MAX_RETRIES: int = 10  # CLI-specific limit

# Entity limits - delegate to flext-core
MAX_ENTITY_NAME_LENGTH: int = FlextConstants.Platform.MAX_NAME_LENGTH
MAX_ERROR_MESSAGE_LENGTH: int = FlextConstants.Limits.MAX_STRING_LENGTH


class _CLIConstants:
    """CLI constants namespace for backward compatibility.

    DEPRECATED: Use FlextCliConstants or FlextConstants directly.
    """

    MAX_ENTITY_NAME_LENGTH: int = MAX_ENTITY_NAME_LENGTH
    MAX_ERROR_MESSAGE_LENGTH: int = MAX_ERROR_MESSAGE_LENGTH
    DEFAULT_TIMEOUT: int = DEFAULT_TIMEOUT

    def __getattribute__(self, name: str) -> object:
        """Warn on access to deprecated constants."""
        if not name.startswith("_"):
            warnings.warn(
                f"CLI_CONSTANTS.{name} is deprecated. Use FlextCliConstants.{name} or FlextConstants instead.",
                DeprecationWarning,
                stacklevel=2,
            )
        return super().__getattribute__(name)


# Export constants for backward compatibility
CLI_CONSTANTS = _CLIConstants()


class FlextCliConstants:
    """CLI-specific constants that extend FlextConstants.

    This class provides CLI-specific constants while delegating
    to flext_core.FlextConstants for all shared constants.
    """

    # Delegate to core constants
    Core = FlextConstants.Core
    Errors = FlextConstants.Errors
    Messages = FlextConstants.Messages
    Status = FlextConstants.Status
    Patterns = FlextConstants.Patterns
    Defaults = FlextConstants.Defaults
    Limits = FlextConstants.Limits
    Performance = FlextConstants.Performance
    Configuration = FlextConstants.Configuration
    Infrastructure = FlextConstants.Infrastructure
    Models = FlextConstants.Models
    Observability = FlextConstants.Observability
    Platform = FlextConstants.Platform

    class Cli:
        """CLI-specific constants extending core CLI constants."""

        # Inherit from core
        HELP_ARGS = FlextConstants.Cli.HELP_ARGS
        VERSION_ARGS = FlextConstants.Cli.VERSION_ARGS
        CONFIG_ARGS = FlextConstants.Cli.CONFIG_ARGS
        VERBOSE_ARGS = FlextConstants.Cli.VERBOSE_ARGS
        OUTPUT_FORMATS = FlextConstants.Cli.OUTPUT_FORMATS
        DEFAULT_OUTPUT_FORMAT = FlextConstants.Cli.DEFAULT_OUTPUT_FORMAT
        SUCCESS_EXIT_CODE = FlextConstants.Cli.SUCCESS_EXIT_CODE
        ERROR_EXIT_CODE = FlextConstants.Cli.ERROR_EXIT_CODE
        INVALID_USAGE_EXIT_CODE = FlextConstants.Cli.INVALID_USAGE_EXIT_CODE

        # CLI-specific additions
        PROFILE_ARGS: ClassVar[list[str]] = ["--profile", "-p"]
        DEBUG_ARGS: ClassVar[list[str]] = ["--debug", "-d"]
        QUIET_ARGS: ClassVar[list[str]] = ["--quiet", "-q"]
        FORCE_ARGS: ClassVar[list[str]] = ["--force", "-f"]

        # Rich output formats
        RICH_FORMATS: ClassVar[list[str]] = ["rich", "table", "tree", "panel"]
        DEFAULT_RICH_FORMAT = "table"

        # Interactive mode
        INTERACTIVE_ARGS: ClassVar[list[str]] = ["--interactive", "-i"]
        INTERACTIVE_PROMPT = "flext> "

        # Command categories
        COMMAND_CATEGORIES: ClassVar[list[str]] = [
            "auth",
            "config",
            "pipeline",
            "service",
            "debug",
            "REDACTED_LDAP_BIND_PASSWORD",
        ]

    class Validation:
        """CLI-specific validation constants."""

        # Command validation
        MIN_COMMAND_LENGTH = 1
        MAX_COMMAND_LENGTH = MAX_COMMAND_LENGTH

        # Input validation
        MIN_INPUT_LENGTH = 1
        MAX_INPUT_LENGTH = FlextConstants.Limits.MAX_STRING_LENGTH

        # Prompt validation
        MIN_PROMPT_LENGTH = 1
        MAX_PROMPT_LENGTH = MAX_PROMPT_LENGTH

        # File path validation
        MAX_PATH_LENGTH = 4096

    class Display:
        """CLI display constants."""

        # Terminal dimensions
        DEFAULT_TERMINAL_WIDTH = 80
        DEFAULT_TERMINAL_HEIGHT = 24
        MIN_TERMINAL_WIDTH = 40

        # Table display
        DEFAULT_TABLE_WIDTH = 120
        MAX_COLUMN_WIDTH = 50

        # Progress indicators
        SPINNER_STYLE = "dots"
        PROGRESS_BAR_WIDTH = 40

        # Colors (Rich color names)
        SUCCESS_COLOR = "green"
        ERROR_COLOR = "red"
        WARNING_COLOR = "yellow"
        INFO_COLOR = "blue"
        DEBUG_COLOR = "magenta"

    class Examples:
        """Constants for examples and demos."""

        # Mock API failure rate (for examples only)
        MOCK_API_FAILURE_RATE = 0.3  # 30% chance of failure for demo purposes


class FlextConfigSemanticConstants:
    """Configuration semantic constants.

    DEPRECATED: Use FlextConstants.Configuration or FlextCliConstants.Configuration instead.
    This class is kept for backward compatibility only.
    """

    def __init__(self) -> None:
        """Warn on instantiation."""
        warnings.warn(
            "FlextConfigSemanticConstants is deprecated. Use FlextConstants.Configuration instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    class Hierarchy:
        """Configuration precedence priorities."""

        CLI_ARGS = FlextConstants.Configuration.CLI_PRIORITY
        ENV_VARS = FlextConstants.Configuration.ENV_PRIORITY
        ENV_FILES = FlextConstants.Configuration.DOTENV_PRIORITY
        CONFIG_FILES = FlextConstants.Configuration.CONFIG_FILE_PRIORITY
        CONSTANTS = FlextConstants.Configuration.CONSTANTS_PRIORITY

    class Sources:
        """Configuration source identifiers."""

        CLI = "cli_args"
        ENVIRONMENT = "environment"
        ENV_FILE = "env_file"
        CONFIG = "config_file"
        DEFAULT = "constants"

    class Files:
        """Standard configuration file patterns."""

        DOTENV_FILES = FlextConstants.Configuration.DOTENV_FILES
        CONFIG_FILES = FlextConstants.Configuration.CONFIG_FILES

    class Types:
        """Configuration value types."""

        STRING = "string"
        INTEGER = "integer"
        BOOLEAN = "boolean"
        LIST = "list"
        DICT = "dict"
        PATH = "path"

    class Formats:
        """Supported configuration file formats."""

        JSON = "json"
        YAML = "yaml"
        TOML = "toml"
        ENV = "env"

    class Validation:
        """Configuration validation constants."""

        REQUIRED = "required"
        OPTIONAL = "optional"
        DEFAULT_PROVIDED = "default_provided"
