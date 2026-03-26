"""Command execution and configuration bridge for flext-cli.

Encapsulates the bridge between registered commands, file utilities, and configuration
helpers using `r` for predictable success/failure handling.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from typing import override

from flext_core import r
from rich.errors import ConsoleError, LiveError, StyleError

from flext_cli import (
    FlextCliFileTools,
    FlextCliServiceBase,
    FlextCliTypes,
    FlextCliUtilities,
    c,
    m,
)


class FlextCliCmd(FlextCliServiceBase):
    """Execute registered CLI commands and expose execution metadata.

    Business Rules:
    ───────────────
    1. Command execution MUST validate configuration before execution
    2. Configuration validation MUST check structure and required fields
    3. Configuration paths MUST be resolved from environment or defaults
    4. Configuration values MUST be persisted to config files
    5. All operations MUST use r[T] for error handling
    6. File operations MUST use FlextCliFileTools for consistency
    7. Config operations MUST delegate to FlextCliUtilities.Cli.ConfigOps
    8. Command execution MUST log all operations for audit trail

    Architecture Implications:
    ───────────────────────────
    - Extends FlextCliServiceBase for consistent logging and container access
    - Delegates file operations to FlextCliFileTools (SRP)
    - Delegates config operations to FlextCliUtilities.Cli.ConfigOps (SRP)
    - Railway-Oriented Programming via r for composable error handling
    - Static methods for stateless operations

    Audit Implications:
    ───────────────────
    - Configuration validation MUST be logged with validation results
    - Configuration changes MUST be logged with key, value (no sensitive data)
    - Configuration path resolution MUST be logged for debugging
    - File operations MUST be logged with file paths (no sensitive content)
    - Command execution failures MUST be logged with full context

    # Attributes initialized in __init__ (inherit types from FlextService)
    # Logger is provided by FlextMixins mixin
    # All config utilities moved to FlextCliUtilities.Cli.ConfigOps
    """

    @override
    def __init__(self) -> None:
        """Initialize the command service and supporting file helpers."""
        super().__init__(
            config_type=None,
            config_overrides=None,
            initial_context=None,
        )
        self._file_tools = FlextCliFileTools()

    @staticmethod
    def get_config_info() -> r[m.Cli.ConfigSnapshot]:
        """Get configuration information using FlextCliUtilities directly."""
        return FlextCliUtilities.try_(
            FlextCliUtilities.Cli.ConfigOps.get_config_info,
        ).map_error(
            lambda e: c.Cli.ErrorMessages.CONFIG_INFO_FAILED.format(
                error=e,
            ),
        )

    @override
    def execute(self) -> r[Mapping[str, FlextCliTypes.Cli.JsonValue]]:
        """Report operational status required by `FlextService`."""
        return r[Mapping[str, FlextCliTypes.Cli.JsonValue]].ok({
            c.Cli.DictKeys.STATUS: c.Cli.ServiceStatus.OPERATIONAL.value,
            c.Cli.DictKeys.SERVICE: c.Cli.CmdDefaults.SERVICE_NAME,
        })

    def show_config(self) -> r[bool]:
        """Show current configuration.

        Returns:
            r[bool]: True if displayed successfully, or error

        """
        try:
            info_result = self.get_config_info()
            if info_result.is_failure:
                return r[bool].fail(
                    c.Cli.CmdErrorMessages.SHOW_CONFIG_FAILED.format(
                        error=info_result.error,
                    ),
                )
            self.logger.info(
                c.Cli.LogMessages.CONFIG_DISPLAYED,
                config=info_result.value,
            )
            return r[bool].ok(value=True)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            return r[bool].fail(
                c.Cli.CmdErrorMessages.SHOW_CONFIG_FAILED.format(
                    error=e,
                ),
            )

    def validate_config(self) -> r[bool]:
        """Validate configuration structure using FlextCliUtilities directly.

        Returns:
            r[bool]: True if validation passed, or error

        """
        try:
            results = FlextCliUtilities.Cli.ConfigOps.validate_config_structure()
            if results:
                self.logger.info(
                    c.Cli.LogMessages.CONFIG_VALIDATION_RESULTS.format(
                        results=results,
                    ),
                )
            return r[bool].ok(value=True)
        except (OSError, ValueError, TypeError, RuntimeError) as e:
            return r[bool].fail(
                c.Cli.ErrorMessages.CONFIG_VALIDATION_FAILED.format(
                    error=e,
                ),
            )


__all__ = ["FlextCliCmd"]
