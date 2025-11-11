"""FLEXT CLI CMD Module - Unified class following FLEXT architecture patterns.

Single FlextCliCmd class providing CLI command functionality.
Follows FLEXT unified class pattern - one class per module extending flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from datetime import UTC, datetime
from pathlib import Path
from typing import override

from flext_core import FlextResult, FlextService, FlextTypes

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.utilities import FlextCliUtilities


class FlextCliCmd(FlextService[FlextTypes.JsonDict]):
    """CMD service extending FlextService from flext-core.

    Provides essential command functionality using flext-core patterns.
    Follows single-responsibility principle with nested helpers.
    """

    # Attributes initialized in __init__ (inherit types from FlextService)
    # Logger is provided by FlextMixins mixin
    # All config utilities moved to FlextCliUtilities.ConfigOps

    @override
    def __init__(self) -> None:
        """Initialize command service with flext-core integration and Phase 1 context enrichment."""
        super().__init__()
        # Logger is automatically provided by FlextMixins mixin
        self._file_tools = FlextCliFileTools()

    def execute(self) -> FlextResult[FlextTypes.JsonDict]:
        """Execute command service - required by FlextService."""
        return FlextResult[FlextTypes.JsonDict].ok({
            FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
            FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.CmdDefaults.SERVICE_NAME,
        })

    @classmethod
    def create_instance(cls) -> "FlextCliCmd":
        """Create new instance of FlextCliCmd."""
        return cls()

    def show_config_paths(self) -> FlextResult[list[str]]:
        """Show configuration paths using FlextCliUtilities directly."""
        try:
            paths = FlextCliUtilities.ConfigOps.get_config_paths()
            return FlextResult[list[str]].ok(paths)
        except Exception as e:
            return FlextResult[list[str]].fail(
                FlextCliConstants.ErrorMessages.CONFIG_PATHS_FAILED.format(error=e)
            )

    def validate_config(self) -> FlextResult[None]:
        """Validate configuration structure using FlextCliUtilities directly."""
        try:
            results = FlextCliUtilities.ConfigOps.validate_config_structure()
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

    def get_config_info(self) -> FlextResult[FlextTypes.JsonDict]:
        """Get configuration information using FlextCliUtilities directly."""
        try:
            info = FlextCliUtilities.ConfigOps.get_config_info()
            return FlextResult[FlextTypes.JsonDict].ok(info)
        except Exception as e:
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.ErrorMessages.CONFIG_INFO_FAILED.format(error=e)
            )

    def set_config_value(self, key: str, value: str) -> FlextResult[bool]:
        """Set configuration value with real persistence using flext-core."""
        try:
            # Use flext-core configuration system for real persistence

            # Set the configuration value using flext-core utilities

            # Create configuration data - key and value are strings, directly JSON-compatible
            config_data: FlextTypes.JsonValue = {key: value}

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
                    FlextCliConstants.CmdErrorMessages.CONFIG_SAVE_FAILED.format(
                        error=save_result.error
                    )
                )

            if self.logger:
                self.logger.info(
                    FlextCliConstants.CmdMessages.CONFIG_SAVED.format(
                        key=key, value=value
                    )
                )
            return FlextResult[bool].ok(True)

        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.SET_CONFIG_FAILED.format(error=e)
            )

    def get_config_value(self, key: str) -> FlextResult[FlextTypes.JsonDict]:
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
                return FlextResult[FlextTypes.JsonDict].fail(
                    FlextCliConstants.CmdErrorMessages.CONFIG_FILE_NOT_FOUND.format(
                        path=config_path
                    )
                )

            # Load configuration data using FlextCliFileTools
            load_result = self._file_tools.read_json_file(str(config_path))
            if load_result.is_failure:
                return FlextResult[FlextTypes.JsonDict].fail(
                    FlextCliConstants.CmdErrorMessages.CONFIG_LOAD_FAILED.format(
                        error=load_result.error
                    )
                )

            config_data = load_result.value

            # Ensure config_data is a dict
            if not isinstance(config_data, dict):
                return FlextResult[FlextTypes.JsonDict].fail(
                    FlextCliConstants.CmdErrorMessages.CONFIG_NOT_DICT
                )

            # Get the specific key value
            if key not in config_data:
                return FlextResult[FlextTypes.JsonDict].fail(
                    FlextCliConstants.CmdErrorMessages.CONFIG_KEY_NOT_FOUND.format(
                        key=key
                    )
                )

            # Cast to proper JsonValue type
            value: FlextTypes.JsonValue = config_data[key]
            result_data: FlextTypes.JsonDict = {
                FlextCliConstants.DictKeys.KEY: key,
                FlextCliConstants.DictKeys.VALUE: value,
                FlextCliConstants.DictKeys.TIMESTAMP: datetime.now(UTC).isoformat(),
            }
            return FlextResult[FlextTypes.JsonDict].ok(result_data)

        except Exception as e:
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.CmdErrorMessages.GET_CONFIG_FAILED.format(error=e)
            )

    def show_config(self) -> FlextResult[None]:
        """Show current configuration."""
        try:
            info_result = self.get_config_info()
            if info_result.is_failure:
                return FlextResult[None].fail(
                    FlextCliConstants.CmdErrorMessages.SHOW_CONFIG_FAILED.format(
                        error=info_result.error
                    )
                )

            if self.logger:
                self.logger.info(
                    FlextCliConstants.LogMessages.CONFIG_DISPLAYED,
                    config=info_result.value,
                )
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(
                FlextCliConstants.CmdErrorMessages.SHOW_CONFIG_FAILED.format(error=e)
            )

    def edit_config(self) -> FlextResult[str]:
        """Edit configuration with extracted helpers and railway pattern."""
        try:
            config_path = (
                FlextCliConfig().config_dir
                / FlextCliConstants.ConfigFiles.CLI_CONFIG_JSON
            )

            # Railway pattern: ensure exists → load → validate → build response
            return (
                self._ensure_config_exists(config_path)
                .flat_map(lambda _: self._load_and_validate_config(config_path))
                .map(lambda config: self._build_config_response(config_path, config))
            )

        except Exception as e:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.EDIT_CONFIG_FAILED.format(error=e)
            )

    def _ensure_config_exists(self, config_path: object) -> FlextResult[None]:
        """Ensure config file exists, create default if not."""
        path = Path(str(config_path))
        if path.exists():
            return FlextResult[None].ok(None)

        # Create default config and save
        default_config = self._create_default_config()
        save_result = self._file_tools.write_json_file(
            file_path=str(path), data=default_config
        )

        if save_result.is_failure:
            return FlextResult[None].fail(
                FlextCliConstants.CmdErrorMessages.CREATE_DEFAULT_CONFIG_FAILED.format(
                    error=save_result.error
                )
            )

        return FlextResult[None].ok(None)

    def _create_default_config(self) -> FlextTypes.JsonValue:
        """Create default configuration dict with proper types."""
        # Build default config with typed values
        host_default: str = str(FlextCliConstants.NetworkDefaults.DEFAULT_HOST)
        port_default: int = int(FlextCliConstants.NetworkDefaults.DEFAULT_PORT)
        timeout_default: int = int(FlextCliConstants.TIMEOUTS.DEFAULT)

        # Create JSON-compatible config
        config_data: FlextTypes.JsonValue = {
            FlextCliConstants.DictKeys.HOST: host_default,
            FlextCliConstants.DictKeys.PORT: port_default,
            FlextCliConstants.DictKeys.TIMEOUT: timeout_default,
        }

        return config_data

    def _load_and_validate_config(
        self, config_path: object
    ) -> FlextResult[FlextTypes.JsonDict]:
        """Load config file and validate it's a dict."""
        load_result = self._file_tools.read_json_file(str(config_path))

        if load_result.is_failure:
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.CmdErrorMessages.CONFIG_LOAD_FAILED.format(
                    error=load_result.error
                )
            )

        # Type guard validation
        if not isinstance(load_result.value, dict):
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.CmdErrorMessages.CONFIG_NOT_DICT
            )

        return FlextResult[FlextTypes.JsonDict].ok(load_result.value)

    def _build_config_response(
        self, config_path: object, config_data: FlextTypes.JsonDict
    ) -> str:
        """Build final config response with logging."""
        config_info = {
            FlextCliConstants.DictKeys.CONFIG_FILE: str(config_path),
            FlextCliConstants.DictKeys.CONFIG_DATA: config_data,
            FlextCliConstants.DictKeys.MESSAGE: FlextCliConstants.ServiceMessages.CONFIG_LOADED_SUCCESSFULLY,
        }

        if self.logger:
            self.logger.info(
                FlextCliConstants.CmdMessages.CONFIG_EDIT_COMPLETED_LOG,
                config=config_info,
            )

        return FlextCliConstants.LogMessages.CONFIG_EDIT_COMPLETED


__all__ = [
    "FlextCliCmd",
]
