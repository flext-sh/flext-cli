"""FLEXT CLI CMD Module.

This module provides aliases for CLI configuration functionality.
All cmd functionality was refactored into FlextCliConfig for better architecture.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextDomainService, FlextLogger, FlextResult

from flext_cli.cli_bus import FlextCliCommandBusService
from flext_cli.config import FlextCliConfig


class FlextCliCmd(FlextDomainService[str]):
    """DEPRECATED - CLI command service replaced by flext-core Command System.

    This class violates SOLID principles by duplicating functionality
    that already exists in flext-core's Command System.

    USE INSTEAD:
    - FlextCliCommandBusService for command execution
    - FlextCommands.Models.Command for command definitions
    - FlextCommands.Handlers.CommandHandler for handlers

    This class is kept only for backward compatibility and will be removed.
    """

    def __init__(self) -> None:
        """Initialize deprecated FlextCliCmd service."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._logger.warning(
            "FlextCliCmd is DEPRECATED. Use FlextCliCommandBusService with flext-core Commands instead."
        )
        # Use proper replacement - avoid import in __init__ to fix PLC0415
        self._command_bus_service = None

    def execute(self) -> FlextResult[str]:
        """Execute deprecated CLI command - replaced by Command Bus."""
        self._logger.warning(
            "FlextCliCmd.execute() is deprecated. Use FlextCliCommandBusService methods instead."
        )
        return FlextResult[str].ok(
            "Use FlextCliCommandBusService for proper Command Bus integration"
        )

    class _ConfigDisplayHelper:
        """DEPRECATED - Use ShowConfigCommandHandler instead."""

        @staticmethod
        def show_config(logger: FlextLogger) -> FlextResult[None]:
            """DEPRECATED - Use ShowConfigCommand with Command Bus."""
            logger.warning(
                "_ConfigDisplayHelper is deprecated. Use ShowConfigCommand instead."
            )
            return FlextResult[None].fail(
                "Use ShowConfigCommand with FlextCliCommandBusService"
            )

    class _ConfigModificationHelper:
        """DEPRECATED - Use SetConfigValueCommandHandler and EditConfigCommandHandler instead."""

        @staticmethod
        def edit_config() -> FlextResult[str]:
            """DEPRECATED - Use EditConfigCommand with Command Bus."""
            return FlextResult[str].fail(
                "Use EditConfigCommand with FlextCliCommandBusService"
            )

    class _ConfigValidationHelper:
        """DEPRECATED - Use configuration validation in Command handlers instead."""

        # DEPRECATED - removed due to undefined references

    def show_config_paths(self) -> FlextResult[list[str]]:
        """Show configuration paths - DEPRECATED."""
        try:
            config = FlextCliConfig()
            paths = [
                str(config.config_dir),
                str(config.cache_dir),
                str(config.token_file),
                str(config.refresh_token_file),
            ]
            return FlextResult[list[str]].ok(paths)
        except Exception as e:
            return FlextResult[list[str]].fail(f"Show config paths failed: {e}")

    def set_config_value(self, key: str, value: str, /) -> FlextResult[str]:
        """DEPRECATED - Use SetConfigValueCommand with FlextCliCommandBusService instead."""
        del key, value  # Mark as intentionally unused
        return FlextResult[str].fail("DEPRECATED - Use SetConfigValueCommand instead")

    def get_config_value(self, key: str | None, /) -> FlextResult[str]:
        """DEPRECATED - Use ShowConfigCommand with FlextCliCommandBusService instead."""
        del key  # Mark as intentionally unused
        return FlextResult[str].fail("DEPRECATED - Use ShowConfigCommand instead")

    def show_config_paths_legacy(
        self, _obj: dict[str, object] | None
    ) -> FlextResult[list[str]]:
        """DEPRECATED - Use show_config_paths() without obj parameter."""
        return self.show_config_paths()


def _get_cmd_instance() -> FlextCliCommandBusService:
    """Get command bus service instance - replacement for deprecated FlextCliCmd."""
    return FlextCliCommandBusService()


# Compatibility aliases for legacy code - DEPRECATED
show_config = FlextCliCmd._ConfigDisplayHelper.show_config
edit_config = FlextCliCmd._ConfigModificationHelper.edit_config


def get_cmd_instance() -> FlextCliCommandBusService:
    """Get CLI command service instance - returns Command Bus Service."""
    return _get_cmd_instance()
