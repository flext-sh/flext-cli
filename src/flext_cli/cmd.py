"""FLEXT CLI CMD Module - Unified class following FLEXT architecture patterns.

Single FlextCliCmd class providing CLI command functionality.
Follows FLEXT unified class pattern - one class per module extending flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import typing
from pathlib import Path
from typing import override

from flext_core import (
    FlextMixins,
    FlextResult,
    FlextRuntime,
    FlextService,
    FlextTypes,
    FlextUtilities,
)

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.models import FlextCliModels
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

    def execute(self, **_kwargs: object) -> FlextResult[FlextTypes.JsonDict]:
        """Execute command service - required by FlextService.

        Args:
            **_kwargs: Additional execution parameters (unused, for FlextService compatibility)

        """
        return FlextResult[FlextTypes.JsonDict].ok({
            FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
            FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.CmdDefaults.SERVICE_NAME,
        })

    def show_config_paths(self) -> FlextResult[list[str]]:
        """Show configuration paths using FlextCliUtilities directly."""
        try:
            paths = FlextCliUtilities.ConfigOps.get_config_paths()
            return FlextResult[list[str]].ok(paths)
        except Exception as e:
            return FlextResult[list[str]].fail(
                FlextCliConstants.ErrorMessages.CONFIG_PATHS_FAILED.format(error=e)
            )

    def validate_config(self) -> FlextResult[bool]:
        """Validate configuration structure using FlextCliUtilities directly.

        Returns:
            FlextResult[bool]: True if validation passed, or error

        """
        try:
            results = FlextCliUtilities.ConfigOps.validate_config_structure()
            if results:
                # Use logger directly from FlextService - no fallback
                self.logger.info(
                    FlextCliConstants.LogMessages.CONFIG_VALIDATION_RESULTS.format(
                        results=results
                    )
                )
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(
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
                FlextCliConfig.get_instance().config_dir
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

            # Use logger directly from FlextService - no fallback
            self.logger.info(
                FlextCliConstants.CmdMessages.CONFIG_SAVED.format(key=key, value=value)
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
                FlextCliConfig.get_instance().config_dir
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
            if not FlextRuntime.is_dict_like(config_data):
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

            # config_data is JsonDict (dict[str, JsonValue]), so config_data[key] is already JsonValue
            value = config_data[key]
            # Cast to JsonDict for type checker (dict with JsonValue values is JsonDict at runtime)
            result_data = typing.cast(
                "FlextTypes.JsonDict",
                {
                    FlextCliConstants.DictKeys.KEY: key,
                    FlextCliConstants.DictKeys.VALUE: value,
                    FlextCliConstants.DictKeys.TIMESTAMP: FlextUtilities.Generators.generate_iso_timestamp(),
                },
            )
            return FlextResult[FlextTypes.JsonDict].ok(result_data)

        except Exception as e:
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.CmdErrorMessages.GET_CONFIG_FAILED.format(error=e)
            )

    def show_config(self) -> FlextResult[bool]:
        """Show current configuration.

        Returns:
            FlextResult[bool]: True if displayed successfully, or error

        """
        try:
            info_result = self.get_config_info()
            if info_result.is_failure:
                return FlextResult[bool].fail(
                    FlextCliConstants.CmdErrorMessages.SHOW_CONFIG_FAILED.format(
                        error=info_result.error
                    )
                )

            # Use logger directly from FlextService - no fallback
            self.logger.info(
                FlextCliConstants.LogMessages.CONFIG_DISPLAYED,
                config=info_result.value,
            )
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.CmdErrorMessages.SHOW_CONFIG_FAILED.format(error=e)
            )

    def edit_config(self) -> FlextResult[str]:
        """Edit configuration using Pydantic validation - no wrappers."""
        try:
            config_path = (
                FlextCliConfig.get_instance().config_dir
                / FlextCliConstants.ConfigFiles.CLI_CONFIG_JSON
            )
            path = Path(str(config_path))

            # Ensure config exists - create default if not
            if not path.exists():
                # Use Pydantic model for default - no conversion needed
                default_config_model = FlextCliModels.CmdConfig()
                save_result = self._file_tools.write_json_file(
                    file_path=str(path),
                    data=FlextMixins.ModelConversion.to_dict(default_config_model),
                )
                if save_result.is_failure:
                    return FlextResult[str].fail(
                        FlextCliConstants.CmdErrorMessages.CREATE_DEFAULT_CONFIG_FAILED.format(
                            error=save_result.error
                        )
                    )

            # Load and validate using Pydantic - use model directly
            load_result = self._file_tools.read_json_file(str(path))
            if load_result.is_failure:
                return FlextResult[str].fail(
                    FlextCliConstants.CmdErrorMessages.CONFIG_LOAD_FAILED.format(
                        error=load_result.error
                    )
                )

            # Validate with Pydantic model - use model directly, no conversion
            try:
                config_model = FlextCliModels.CmdConfig.model_validate(
                    load_result.value
                )
            except Exception:
                return FlextResult[str].fail(
                    FlextCliConstants.CmdErrorMessages.CONFIG_NOT_DICT
                )

            # Use model directly - no conversion needed
            config_data = FlextMixins.ModelConversion.to_dict(config_model)

            # Build response - replaces _build_config_response
            config_info = {
                FlextCliConstants.DictKeys.CONFIG_FILE: str(path),
                FlextCliConstants.DictKeys.CONFIG_DATA: config_data,
                FlextCliConstants.DictKeys.MESSAGE: FlextCliConstants.ServiceMessages.CONFIG_LOADED_SUCCESSFULLY,
            }

            # Use logger directly from FlextService - no fallback
            self.logger.info(
                FlextCliConstants.CmdMessages.CONFIG_EDIT_COMPLETED_LOG,
                config=config_info,
            )

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
