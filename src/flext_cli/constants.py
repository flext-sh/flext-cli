"""FLEXT CLI Constants - Zero Boilerplate Configuration Values.

Modern constants following foundation-refactored.md patterns.
Eliminates duplication across configuration modules.

Foundation Pattern Applied:
    # NEW: Self-documenting constants with type safety
    DEFAULT_API_URL: str = "http://localhost:8000"
    DEFAULT_TIMEOUT: int = 30

Architecture:
    - Type-safe constant definitions
    - Single source of truth for defaults
    - Integration with environment variables
    - Zero boilerplate constant management

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

# API defaults
DEFAULT_API_URL: str = "http://localhost:8000"
DEFAULT_TIMEOUT: int = 30
DEFAULT_RETRIES: int = 3

# Output defaults
DEFAULT_OUTPUT_FORMAT: str = "table"
DEFAULT_LOG_LEVEL: str = "INFO"

# CLI behavior
DEFAULT_PROFILE: str = "default"
DEFAULT_DEBUG: bool = False

# Environment configuration
ENV_PREFIX: str = "FLEXT_CLI_"
ENV_FILE: str = ".env"

# Validation limits
MAX_TIMEOUT: int = 300
MIN_TIMEOUT: int = 1
MAX_RETRIES: int = 10

# Entity limits
MAX_ENTITY_NAME_LENGTH: int = 255
MAX_ERROR_MESSAGE_LENGTH: int = 1000


class _CLIConstants:
    """CLI constants namespace for backward compatibility."""

    MAX_ENTITY_NAME_LENGTH: int = MAX_ENTITY_NAME_LENGTH
    MAX_ERROR_MESSAGE_LENGTH: int = MAX_ERROR_MESSAGE_LENGTH
    DEFAULT_TIMEOUT: int = DEFAULT_TIMEOUT


# Export constants for backward compatibility
CLI_CONSTANTS = _CLIConstants()


class FlextConfigSemanticConstants:
    """Configuration semantic constants following docs/patterns/config-cli.md."""

    class Hierarchy:
        """Configuration precedence priorities."""

        CLI_ARGS = 1      # Highest precedence
        ENV_VARS = 2
        ENV_FILES = 3
        CONFIG_FILES = 4
        CONSTANTS = 5     # Lowest precedence

    class Sources:
        """Configuration source identifiers."""

        CLI = "cli_args"
        ENVIRONMENT = "environment"
        ENV_FILE = "env_file"
        CONFIG = "config_file"
        DEFAULT = "constants"

    class Files:
        """Standard configuration file patterns."""

        DOTENV_FILES: ClassVar[list[str]] = [".env", ".internal.invalid", ".env.development", ".env.production"]
        CONFIG_FILES: ClassVar[list[str]] = ["config.json", "config.yaml", "config.toml", "pyproject.toml"]

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
