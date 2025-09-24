"""FLEXT CLI Typings - Single unified class following FLEXT standards.

Provides CLI-specific type definitions using flext-core patterns.
Single FlextCliTypings class with nested type definitions following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TypeVar

from flext_core import FlextTypes


class FlextCliTypings(FlextTypes):
    """Single unified CLI typings class following FLEXT standards.

    Contains all type definitions for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested definitions.
    """

    # Type variables for CLI generics
    T = TypeVar("T")
    CommandHandler = TypeVar("CommandHandler")

    # CLI-specific type aliases extending flext-core using Python 3.13+ type keyword
    type CliConfigData = FlextTypes.Core.Dict
    type CliCommandArgs = FlextTypes.Core.Dict
    type CliCommandResult = FlextTypes.Core.Dict
    type CliFormatData = FlextTypes.Core.Dict

    # CLI output format types
    type OutputFormatType = str
    type CliExitCode = int

    # CLI command handler types
    type CommandHandlerFunc = object  # Will be more specific when protocols are defined

    # CLI authentication types
    type AuthTokenData = FlextTypes.Core.Dict
    type AuthConfigData = FlextTypes.Core.Dict

    # CLI debug and logging types
    type DebugInfoData = FlextTypes.Core.Dict
    type LoggingConfigData = FlextTypes.Core.Dict

    class OutputFormat:
        """Output format constants for CLI operations."""

        JSON = "json"
        YAML = "yaml"
        CSV = "csv"
        TABLE = "table"
        PLAIN = "plain"

        @classmethod
        def get_all_formats(cls) -> dict[str, str]:
            """Return all format options."""
            return {
                "JSON": cls.JSON,
                "YAML": cls.YAML,
                "CSV": cls.CSV,
                "TABLE": cls.TABLE,
                "PLAIN": cls.PLAIN,
            }

    class Commands:
        """CLI command constants."""

        AUTH = "auth"
        CONFIG = "config"
        DEBUG = "debug"
        FORMAT = "format"
        EXPORT = "export"

    class CliConfig:
        """CLI configuration constants."""

        DEFAULT_PROFILE = "default"
        DEFAULT_OUTPUT_FORMAT = "table"
        DEFAULT_TIMEOUT = 30

    class Auth:
        """CLI authentication constants."""

        TOKEN_FILENAME = "token.json"  # noqa: S105
        CONFIG_FILENAME = "auth.json"

    class Session:
        """CLI session constants."""

        DEFAULT_TIMEOUT = 3600
        MAX_COMMANDS = 1000

    class Services:
        """CLI service constants."""

        API = "api"
        FORMATTER = "formatter"
        AUTH = "auth"

    class Protocols:
        """CLI protocol constants."""

        HTTP = "http"
        HTTPS = "https"


__all__ = [
    "FlextCliTypings",
]
