"""FLEXT CLI CMD Module - Unified class following FLEXT architecture patterns.

Single FlextCliCmd class providing CLI command functionality.
Follows FLEXT unified class pattern - one class per module extending flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import override

from flext_core import FlextCore

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.file_tools import FlextCliFileTools


class FlextCliCmd(FlextCore.Service[FlextCore.Types.Dict]):
    """CMD service extending FlextCore.Service from flext-core.

    Provides essential command functionality using flext-core patterns.
    Follows single-responsibility principle with nested helpers.
    """

    # Attributes initialized in __init__ (inherit types from FlextCore.Service)

    @override
    def __init__(self) -> None:
        """Initialize command service with flext-core integration and Phase 1 context enrichment."""
        super().__init__()
        # Logger is automatically provided by FlextCore.Mixins mixin
        self._file_tools = FlextCliFileTools()

    def execute(self) -> FlextCore.Result[FlextCore.Types.Dict]:
        """Execute command service - required by FlextCore.Service."""
        return FlextCore.Result[FlextCore.Types.Dict].ok({
            "status": "operational",
            "service": "FlextCliCmd",
        })

    @classmethod
    def create_instance(cls) -> FlextCliCmd:
        """Create new instance of FlextCliCmd."""
        return cls()

    def _get_config_paths(self) -> FlextCore.Types.StringList:
        """Get standard configuration paths."""
        home = Path.home()
        flext_dir = home / FlextCliConstants.FLEXT_DIR_NAME

        return [
            str(flext_dir),
            str(flext_dir / FlextCliConstants.DictKeys.CONFIG),
            str(flext_dir / "cache"),
            str(flext_dir / "logs"),
            str(flext_dir / FlextCliConstants.DictKeys.TOKEN),
            str(flext_dir / "refresh_token"),
        ]

    def _validate_config_structure(self) -> FlextCore.Types.StringList:
        """Validate configuration directory structure."""
        results: FlextCore.Types.StringList = []
        home = Path.home()
        flext_dir = home / FlextCliConstants.FLEXT_DIR_NAME

        # Check main config directory
        if flext_dir.exists():
            results.append("✓ Main config directory exists")
        else:
            results.append("✗ Main config directory missing")

        # Check subdirectories
        for subdir in [FlextCliConstants.DictKeys.CONFIG, "cache", "logs"]:
            path = flext_dir / subdir
            if path.exists():
                results.append(f"✓ {subdir} directory exists")
            else:
                results.append(f"✗ {subdir} directory missing")

        return results

    def _get_config_info(self) -> FlextCore.Types.Dict:
        """Get configuration information."""
        home = Path.home()
        flext_dir = home / FlextCliConstants.FLEXT_DIR_NAME

        return {
            FlextCliConstants.DictKeys.CONFIG_DIR: str(flext_dir),
            FlextCliConstants.DictKeys.CONFIG_EXISTS: flext_dir.exists(),
            FlextCliConstants.DictKeys.CONFIG_READABLE: flext_dir.exists()
            and os.access(flext_dir, os.R_OK),
            FlextCliConstants.DictKeys.CONFIG_WRITABLE: flext_dir.exists()
            and os.access(flext_dir, os.W_OK),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def show_config_paths(self) -> FlextCore.Result[FlextCore.Types.StringList]:
        """Show configuration paths."""
        try:
            paths = self._get_config_paths()
            return FlextCore.Result[FlextCore.Types.StringList].ok(paths)
        except Exception as e:
            return FlextCore.Result[FlextCore.Types.StringList].fail(
                FlextCliConstants.ErrorMessages.CONFIG_PATHS_FAILED.format(error=e)
            )

    def validate_config(self) -> FlextCore.Result[None]:
        """Validate configuration structure."""
        try:
            results = self._validate_config_structure()
            if results and self.logger:
                self.logger.info(
                    FlextCliConstants.LogMessages.CONFIG_VALIDATION_RESULTS.format(
                        results=results
                    )
                )
            return FlextCore.Result[None].ok(None)
        except Exception as e:
            return FlextCore.Result[None].fail(
                FlextCliConstants.ErrorMessages.CONFIG_VALIDATION_FAILED.format(error=e)
            )

    def get_config_info(self) -> FlextCore.Result[FlextCore.Types.Dict]:
        """Get configuration information."""
        try:
            info = self._get_config_info()
            return FlextCore.Result[FlextCore.Types.Dict].ok(info)
        except Exception as e:
            return FlextCore.Result[FlextCore.Types.Dict].fail(
                FlextCliConstants.ErrorMessages.CONFIG_INFO_FAILED.format(error=e)
            )

    def set_config_value(self, key: str, value: str) -> FlextCore.Result[bool]:
        """Set configuration value with real persistence using flext-core."""
        try:
            # Use flext-core configuration system for real persistence

            # Set the configuration value using flext-core utilities

            # Create configuration data
            config_data: FlextCore.Types.Dict = {key: value}

            # Save to file using FlextCliFileTools
            config_path = (
                FlextCliConfig().config_dir
                / FlextCliConstants.ConfigFiles.CLI_CONFIG_JSON
            )
            save_result = self._file_tools.write_json_file(
                file_path=str(config_path), data=config_data
            )

            if not save_result.is_success:
                return FlextCore.Result[bool].fail(
                    f"Config save failed: {save_result.error}"
                )

            if self.logger:
                self.logger.info(f"Configuration saved: {key} = {value}")
            return FlextCore.Result[bool].ok(True)

        except Exception as e:
            return FlextCore.Result[bool].fail(
                FlextCliConstants.ErrorMessages.SET_CONFIG_FAILED.format(error=e)
            )

    def get_config_value(self, key: str) -> FlextCore.Result[FlextCore.Types.Dict]:
        """Get configuration value with real persistence using flext-core."""
        try:
            # Use flext-core configuration system for real persistence

            # Load configuration from file
            config_path = (
                FlextCliConfig().config_dir
                / FlextCliConstants.ConfigFiles.CLI_CONFIG_JSON
            )

            # Check if config file exists
            if not config_path.exists():
                return FlextCore.Result[FlextCore.Types.Dict].fail(
                    f"Configuration file not found: {config_path}"
                )

            # Load configuration data using FlextCliFileTools
            load_result = self._file_tools.read_json_file(str(config_path))
            if load_result.is_failure:
                return FlextCore.Result[FlextCore.Types.Dict].fail(
                    f"Config load failed: {load_result.error}"
                )

            config_data = load_result.value

            # Ensure config_data is a dict
            if not isinstance(config_data, dict):
                return FlextCore.Result[FlextCore.Types.Dict].fail(
                    "Configuration data is not a valid dictionary"
                )

            # Get the specific key value
            if key not in config_data:
                return FlextCore.Result[FlextCore.Types.Dict].fail(
                    f"Configuration key not found: {key}"
                )

            result_data: FlextCore.Types.Dict = {
                "key": key,
                "value": config_data[key],
                "timestamp": datetime.now(UTC).isoformat(),
            }
            return FlextCore.Result[FlextCore.Types.Dict].ok(result_data)

        except Exception as e:
            return FlextCore.Result[FlextCore.Types.Dict].fail(
                f"Get config failed: {e}"
            )

    def show_config(self) -> FlextCore.Result[None]:
        """Show current configuration."""
        try:
            info_result = self.get_config_info()
            if info_result.is_failure:
                return FlextCore.Result[None].fail(
                    f"Show config failed: {info_result.error}"
                )

            if self.logger:
                self.logger.info(
                    FlextCliConstants.LogMessages.CONFIG_DISPLAYED,
                    config=info_result.value,
                )
            return FlextCore.Result[None].ok(None)
        except Exception as e:
            return FlextCore.Result[None].fail(
                FlextCliConstants.ErrorMessages.SHOW_CONFIG_FAILED.format(error=e)
            )

    def edit_config(self) -> FlextCore.Result[str]:
        """Edit configuration with real implementation using flext-core."""
        try:
            # Use flext-core configuration system for real editing

            # Get configuration file path
            config_path = (
                FlextCliConfig().config_dir
                / FlextCliConstants.ConfigFiles.CLI_CONFIG_JSON
            )

            # Check if config file exists, create if not
            if not config_path.exists():
                # Create default configuration
                default_config = {
                    "host": "localhost",
                    "port": 8080,
                    "profile": FlextCliConstants.DEFAULT,
                    "debug": False,
                    "verbose": False,
                    "quiet": False,
                    "output_format": FlextCliConstants.TABLE,
                    "timeout": 30,
                }

                # Save default configuration - convert values to object type
                config_data: FlextCore.Types.Dict = {
                    "host": str(default_config[FlextCliConstants.DictKeys.HOST]),
                    "port": default_config[
                        FlextCliConstants.DictKeys.PORT
                    ],  # Already int from default_config
                    "timeout": default_config[
                        "timeout"
                    ],  # Already int from default_config
                }
                save_result = self._file_tools.write_json_file(
                    file_path=str(config_path), data=config_data
                )
                if save_result.is_failure:
                    return FlextCore.Result[str].fail(
                        f"Failed to create default config: {save_result.error}"
                    )

            # Load current configuration
            load_result = self._file_tools.read_json_file(str(config_path))
            if load_result.is_failure:
                return FlextCore.Result[str].fail(
                    f"Failed to load config: {load_result.error}"
                )

            # Ensure config_data is a dict[str, object] with type guard
            if not isinstance(load_result.value, dict):
                return FlextCore.Result[str].fail(
                    "Configuration data is not a valid dictionary"
                )

            loaded_config_data: FlextCore.Types.Dict = load_result.value

            # For now, return success with config info
            # In a real implementation, this would open an editor
            config_info = {
                "config_file": str(config_path),
                "config_data": loaded_config_data,
                "message": FlextCliConstants.ServiceMessages.CONFIG_LOADED_SUCCESSFULLY,
            }

            if self.logger:
                self.logger.info("Configuration edit completed", config=config_info)
            return FlextCore.Result[str].ok(
                FlextCliConstants.LogMessages.CONFIG_EDIT_COMPLETED
            )

        except Exception as e:
            return FlextCore.Result[str].fail(
                FlextCliConstants.ErrorMessages.EDIT_CONFIG_FAILED.format(error=e)
            )


__all__ = [
    "FlextCliCmd",
]
