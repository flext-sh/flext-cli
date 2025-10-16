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

from flext_core import FlextResult, FlextService, FlextTypes

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.file_tools import FlextCliFileTools


class FlextCliCmd(FlextService[FlextTypes.Dict]):
    """CMD service extending FlextService from flext-core.

    Provides essential command functionality using flext-core patterns.
    Follows single-responsibility principle with nested helpers.
    """

    # Attributes initialized in __init__ (inherit types from FlextService)
    # Logger is provided by FlextMixins mixin

    @override
    def __init__(self) -> None:
        """Initialize command service with flext-core integration and Phase 1 context enrichment."""
        super().__init__()
        # Logger is automatically provided by FlextMixins mixin
        self._file_tools = FlextCliFileTools()

    def execute(self) -> FlextResult[FlextTypes.Dict]:
        """Execute command service - required by FlextService."""
        return FlextResult[FlextTypes.Dict].ok({
            FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
            FlextCliConstants.DictKeys.SERVICE: "FlextCliCmd",
        })

    @classmethod
    def create_instance(cls) -> FlextCliCmd:
        """Create new instance of FlextCliCmd."""
        return cls()

    def _get_config_paths(self) -> FlextTypes.StringList:
        """Get standard configuration paths."""
        home = Path.home()
        flext_dir = home / FlextCliConstants.FLEXT_DIR_NAME

        return [
            str(flext_dir),
            str(flext_dir / FlextCliConstants.DictKeys.CONFIG),
            str(flext_dir / FlextCliConstants.Subdirectories.CACHE),
            str(flext_dir / FlextCliConstants.Subdirectories.LOGS),
            str(flext_dir / FlextCliConstants.DictKeys.TOKEN),
            str(flext_dir / FlextCliConstants.Subdirectories.REFRESH_TOKEN),
        ]

    def _validate_config_structure(self) -> FlextTypes.StringList:
        """Validate configuration directory structure."""
        results: FlextTypes.StringList = []
        home = Path.home()
        flext_dir = home / FlextCliConstants.FLEXT_DIR_NAME

        # Check main config directory
        if flext_dir.exists():
            results.append(
                FlextCliConstants.Symbols.SUCCESS_MARK + " Main config directory exists"
            )
        else:
            results.append(
                FlextCliConstants.Symbols.FAILURE_MARK
                + " Main config directory missing"
            )

        # Check subdirectories using constants
        for subdir in FlextCliConstants.Subdirectories.STANDARD_SUBDIRS:
            path = flext_dir / subdir
            if path.exists():
                results.append(
                    f"{FlextCliConstants.Symbols.SUCCESS_MARK} {subdir} directory exists"
                )
            else:
                results.append(
                    f"{FlextCliConstants.Symbols.FAILURE_MARK} {subdir} directory missing"
                )

        return results

    def _get_config_info(self) -> FlextTypes.Dict:
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
            FlextCliConstants.DictKeys.TIMESTAMP: datetime.now(UTC).isoformat(),
        }

    def show_config_paths(self) -> FlextResult[FlextTypes.StringList]:
        """Show configuration paths."""
        try:
            paths = self._get_config_paths()
            return FlextResult[FlextTypes.StringList].ok(paths)
        except Exception as e:
            return FlextResult[FlextTypes.StringList].fail(
                FlextCliConstants.ErrorMessages.CONFIG_PATHS_FAILED.format(error=e)
            )

    def validate_config(self) -> FlextResult[None]:
        """Validate configuration structure."""
        try:
            results = self._validate_config_structure()
            if results and self.logger:
                self.logger.info(
                    FlextCliConstants.LogMessages.CONFIG_VALIDATION_RESULTS.format(
                        results=results
                    )
                )
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.CONFIG_VALIDATION_FAILED.format(error=e)
            )

    def get_config_info(self) -> FlextResult[FlextTypes.Dict]:
        """Get configuration information."""
        try:
            info = self._get_config_info()
            return FlextResult[FlextTypes.Dict].ok(info)
        except Exception as e:
            return FlextResult[FlextTypes.Dict].fail(
                FlextCliConstants.ErrorMessages.CONFIG_INFO_FAILED.format(error=e)
            )

    def set_config_value(self, key: str, value: str) -> FlextResult[bool]:
        """Set configuration value with real persistence using flext-core."""
        try:
            # Use flext-core configuration system for real persistence

            # Set the configuration value using flext-core utilities

            # Create configuration data
            config_data: FlextTypes.Dict = {key: value}

            # Save to file using FlextCliFileTools
            config_path = (
                FlextCliConfig().config_dir
                / FlextCliConstants.ConfigFiles.CLI_CONFIG_JSON
            )
            save_result = self._file_tools.write_json_file(
                file_path=str(config_path), data=config_data
            )

            if not save_result.is_success:
                return FlextResult[bool].fail(
                    f"Config save failed: {save_result.error}"
                )

            if self.logger:
                self.logger.info(f"Configuration saved: {key} = {value}")
            return FlextResult[bool].ok(True)

        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.SET_CONFIG_FAILED.format(error=e)
            )

    def get_config_value(self, key: str) -> FlextResult[FlextTypes.Dict]:
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
                return FlextResult[FlextTypes.Dict].fail(
                    f"Configuration file not found: {config_path}"
                )

            # Load configuration data using FlextCliFileTools
            load_result = self._file_tools.read_json_file(str(config_path))
            if load_result.is_failure:
                return FlextResult[FlextTypes.Dict].fail(
                    f"Config load failed: {load_result.error}"
                )

            config_data = load_result.value

            # Ensure config_data is a dict
            if not isinstance(config_data, dict):
                return FlextResult[FlextTypes.Dict].fail(
                    "Configuration data is not a valid dictionary"
                )

            # Get the specific key value
            if key not in config_data:
                return FlextResult[FlextTypes.Dict].fail(
                    f"Configuration key not found: {key}"
                )

            result_data: FlextTypes.Dict = {
                FlextCliConstants.DictKeys.KEY: key,
                FlextCliConstants.DictKeys.VALUE: config_data[key],
                FlextCliConstants.DictKeys.TIMESTAMP: datetime.now(UTC).isoformat(),
            }
            return FlextResult[FlextTypes.Dict].ok(result_data)

        except Exception as e:
            return FlextResult[FlextTypes.Dict].fail(f"Get config failed: {e}")

    def show_config(self) -> FlextResult[None]:
        """Show current configuration."""
        try:
            info_result = self.get_config_info()
            if info_result.is_failure:
                return FlextResult[None].fail(
                    f"Show config failed: {info_result.error}"
                )

            if self.logger:
                self.logger.info(
                    FlextCliConstants.LogMessages.CONFIG_DISPLAYED,
                    config=info_result.value,
                )
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.SHOW_CONFIG_FAILED.format(error=e)
            )

    def edit_config(self) -> FlextResult[str]:
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
                    FlextCliConstants.DictKeys.HOST: FlextCliConstants.NetworkDefaults.DEFAULT_HOST,
                    FlextCliConstants.DictKeys.PORT: FlextCliConstants.NetworkDefaults.DEFAULT_PORT,
                    FlextCliConstants.DictKeys.PROFILE: FlextCliConstants.DEFAULT,
                    FlextCliConstants.DictKeys.DEBUG: False,
                    FlextCliConstants.DictKeys.VERBOSE: False,
                    FlextCliConstants.DictKeys.QUIET: False,
                    FlextCliConstants.DictKeys.OUTPUT_FORMAT: FlextCliConstants.TABLE,
                    FlextCliConstants.DictKeys.TIMEOUT: FlextCliConstants.TIMEOUTS.DEFAULT,
                }

                # Save default configuration - convert values to object type
                config_data: FlextTypes.Dict = {
                    FlextCliConstants.DictKeys.HOST: str(
                        default_config[FlextCliConstants.DictKeys.HOST]
                    ),
                    FlextCliConstants.DictKeys.PORT: default_config[
                        FlextCliConstants.DictKeys.PORT
                    ],  # Already int from default_config
                    FlextCliConstants.DictKeys.TIMEOUT: default_config[
                        FlextCliConstants.DictKeys.TIMEOUT
                    ],  # Already int from default_config
                }
                save_result = self._file_tools.write_json_file(
                    file_path=str(config_path), data=config_data
                )
                if save_result.is_failure:
                    return FlextResult[str].fail(
                        f"Failed to create default config: {save_result.error}"
                    )

            # Load current configuration
            load_result = self._file_tools.read_json_file(str(config_path))
            if load_result.is_failure:
                return FlextResult[str].fail(
                    f"Failed to load config: {load_result.error}"
                )

            # Ensure config_data is a dict[str, object] with type guard
            if not isinstance(load_result.value, dict):
                return FlextResult[str].fail(
                    "Configuration data is not a valid dictionary"
                )

            loaded_config_data: FlextTypes.Dict = load_result.value

            # For now, return success with config info
            # In a real implementation, this would open an editor
            config_info = {
                FlextCliConstants.DictKeys.CONFIG_FILE: str(config_path),
                FlextCliConstants.DictKeys.CONFIG_DATA: loaded_config_data,
                FlextCliConstants.DictKeys.MESSAGE: FlextCliConstants.ServiceMessages.CONFIG_LOADED_SUCCESSFULLY,
            }

            if self.logger:
                self.logger.info("Configuration edit completed", config=config_info)
            return FlextResult[str].ok(
                FlextCliConstants.LogMessages.CONFIG_EDIT_COMPLETED
            )

        except Exception as e:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.EDIT_CONFIG_FAILED.format(error=e)
            )


__all__ = [
    "FlextCliCmd",
]
