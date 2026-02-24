"""Command execution and configuration bridge for flext-cli.

Encapsulates the bridge between registered commands, file utilities, and configuration
helpers using `FlextResult` for predictable success/failure handling.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import override

from flext_core import r, t

from flext_cli.base import FlextCliServiceBase
from flext_cli.constants import FlextCliConstants
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.models import m
from flext_cli.services.output import FlextCliOutput
from flext_cli.utilities import FlextCliUtilities


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
    - Railway-Oriented Programming via FlextResult for composable error handling
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
        super().__init__()
        # Logger is automatically provided by FlextMixins mixin
        self._file_tools = FlextCliFileTools()

    def execute(self) -> r[Mapping[str, t.JsonValue]]:
        """Report operational status required by `FlextService`."""
        return r[Mapping[str, t.JsonValue]].ok({
            FlextCliConstants.Cli.DictKeys.STATUS: FlextCliConstants.Cli.ServiceStatus.OPERATIONAL.value,
            FlextCliConstants.Cli.DictKeys.SERVICE: FlextCliConstants.Cli.CmdDefaults.SERVICE_NAME,
        })

    @staticmethod
    def show_config_paths() -> r[list[str]]:
        """Show configuration paths using FlextCliUtilities directly."""
        try:
            paths = FlextCliUtilities.Cli.ConfigOps.get_config_paths()
            return r[list[str]].ok(paths)
        except (OSError, ValueError, TypeError, RuntimeError) as e:
            return r[list[str]].fail(
                FlextCliConstants.Cli.ErrorMessages.CONFIG_PATHS_FAILED.format(error=e),
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
                    FlextCliConstants.Cli.LogMessages.CONFIG_VALIDATION_RESULTS.format(
                        results=results,
                    ),
                )
            return r[bool].ok(value=True)
        except (OSError, ValueError, TypeError, RuntimeError) as e:
            return r[bool].fail(
                FlextCliConstants.Cli.ErrorMessages.CONFIG_VALIDATION_FAILED.format(
                    error=e,
                ),
            )

    @staticmethod
    def get_config_info() -> r[m.Cli.ConfigSnapshot]:
        """Get configuration information using FlextCliUtilities directly."""
        try:
            info = FlextCliUtilities.Cli.ConfigOps.get_config_info()
            snapshot = m.Cli.ConfigSnapshot(
                config_dir=str(info.get("config_dir", "")),
                config_exists=bool(info.get("config_exists", False)),
                config_readable=bool(info.get("config_readable", False)),
                config_writable=bool(info.get("config_writable", False)),
                timestamp=str(info.get("timestamp", "")),
            )
            return r[m.Cli.ConfigSnapshot].ok(snapshot)
        except (OSError, ValueError, TypeError, RuntimeError, KeyError) as e:
            return r[m.Cli.ConfigSnapshot].fail(
                FlextCliConstants.Cli.ErrorMessages.CONFIG_INFO_FAILED.format(error=e),
            )

    def set_config_value(self, key: str, value: str) -> r[bool]:
        """Set configuration value with real persistence using flext-core."""
        try:
            config_path = (
                FlextCliServiceBase.get_cli_config().config_dir
                / FlextCliConstants.Cli.ConfigFiles.CLI_CONFIG_JSON
            )
            config_data: t.JsonValue = {key: value}
            save_result = self._file_tools.write_json_file(
                file_path=str(config_path),
                data=config_data,
            )

            if save_result.is_failure:
                return r[bool].fail(
                    FlextCliConstants.Cli.CmdErrorMessages.CONFIG_SAVE_FAILED.format(
                        error=save_result.error,
                    ),
                )

            self.logger.info(
                FlextCliConstants.Cli.CmdMessages.CONFIG_SAVED.format(
                    key=key,
                    value=value,
                ),
            )
            return r[bool].ok(value=True)
        except Exception as e:
            return r[bool].fail(
                FlextCliConstants.Cli.ErrorMessages.SET_CONFIG_FAILED.format(error=e),
            )

    def get_config_value(self, key: str) -> r[Mapping[str, t.JsonValue]]:
        """Get configuration value with real persistence using flext-core."""
        try:
            config_path = (
                FlextCliServiceBase.get_cli_config().config_dir
                / FlextCliConstants.Cli.ConfigFiles.CLI_CONFIG_JSON
            )

            if not config_path.exists():
                return r[Mapping[str, t.JsonValue]].fail(
                    FlextCliConstants.Cli.CmdErrorMessages.CONFIG_FILE_NOT_FOUND.format(
                        path=config_path,
                    ),
                )

            load_result = self._file_tools.read_json_file(str(config_path))
            if load_result.is_failure:
                load_error_text = str(load_result.error or "")
                if "Cannot create success result with None value" in load_error_text:
                    return r[Mapping[str, t.JsonValue]].fail(
                        FlextCliConstants.Cli.CmdErrorMessages.CONFIG_NOT_DICT,
                    )
                return r[Mapping[str, t.JsonValue]].fail(
                    FlextCliConstants.Cli.CmdErrorMessages.CONFIG_LOAD_FAILED.format(
                        error=load_result.error,
                    ),
                )

            config_data = load_result.value
            if not FlextCliUtilities.is_dict_like(config_data):
                return r[Mapping[str, t.JsonValue]].fail(
                    FlextCliConstants.Cli.CmdErrorMessages.CONFIG_NOT_DICT,
                )
            if isinstance(config_data, Mapping):
                config_data_dict = {
                    str(key): FlextCliOutput.norm_json(value)
                    for key, value in config_data.items()
                }
            else:
                config_data_dict = {}

            if key not in config_data_dict:
                return r[Mapping[str, t.JsonValue]].fail(
                    FlextCliConstants.Cli.CmdErrorMessages.CONFIG_KEY_NOT_FOUND.format(
                        key=key,
                    ),
                )

            value = config_data_dict[key]
            # Use FlextCliUtilities.transform for JSON conversion
            raw_data = {
                FlextCliConstants.Cli.DictKeys.KEY: key,
                FlextCliConstants.Cli.DictKeys.VALUE: value,
                FlextCliConstants.Cli.DictKeys.TIMESTAMP: FlextCliUtilities.generate(
                    "timestamp",
                ),
            }
            # Python 3.13: to_dict_json() always returns dict, cast_if and isinstance are unnecessary
            # Reuse to_dict_json helper from output module
            result_data: dict[str, t.JsonValue] = dict(
                FlextCliOutput.to_dict_json(raw_data)
            )
            return r[Mapping[str, t.JsonValue]].ok(result_data)
        except Exception as e:
            return r[Mapping[str, t.JsonValue]].fail(
                FlextCliConstants.Cli.CmdErrorMessages.GET_CONFIG_FAILED.format(
                    error=e,
                ),
            )

    def show_config(self) -> r[bool]:
        """Show current configuration.

        Returns:
            r[bool]: True if displayed successfully, or error

        """
        try:
            info_result = self.get_config_info()
            if info_result.is_failure:
                return r[bool].fail(
                    FlextCliConstants.Cli.CmdErrorMessages.SHOW_CONFIG_FAILED.format(
                        error=info_result.error,
                    ),
                )

            self.logger.info(
                FlextCliConstants.Cli.LogMessages.CONFIG_DISPLAYED,
                config=info_result.value,
            )
            return r[bool].ok(value=True)
        except Exception as e:
            return r[bool].fail(
                FlextCliConstants.Cli.CmdErrorMessages.SHOW_CONFIG_FAILED.format(
                    error=e,
                ),
            )

    def edit_config(self) -> r[str]:
        """Edit configuration using Pydantic validation - no wrappers."""
        try:
            config_path = (
                FlextCliServiceBase.get_cli_config().config_dir
                / FlextCliConstants.Cli.ConfigFiles.CLI_CONFIG_JSON
            )
            path = Path(str(config_path))

            if not path.exists():
                default_config_model = m.Cli.CmdConfig(name="default")
                save_result = self._file_tools.write_json_file(
                    file_path=str(path),
                    # JSON file write boundary requires raw JSON-compatible data.
                    data=default_config_model.model_dump(),
                )
                if save_result.is_failure:
                    return r[str].fail(
                        FlextCliConstants.Cli.CmdErrorMessages.CREATE_DEFAULT_CONFIG_FAILED.format(
                            error=save_result.error,
                        ),
                    )

            load_result = self._file_tools.read_json_file(str(path))
            if load_result.is_failure:
                load_error_text = str(load_result.error or "")
                if "Cannot create success result with None value" in load_error_text:
                    return r[str].fail(
                        FlextCliConstants.Cli.CmdErrorMessages.CONFIG_NOT_DICT,
                    )
                return r[str].fail(
                    FlextCliConstants.Cli.CmdErrorMessages.CONFIG_LOAD_FAILED.format(
                        error=load_result.error,
                    ),
                )

            try:
                config_model = m.Cli.CmdConfig.model_validate(
                    load_result.value,
                )
            except Exception as e:
                self.logger.debug(
                    "edit_config model_validate fallback: %s",
                    e,
                    exc_info=False,
                )
                return r[str].fail(
                    FlextCliConstants.Cli.CmdErrorMessages.CONFIG_NOT_DICT,
                )

            config_info_str = str({
                FlextCliConstants.Cli.DictKeys.CONFIG_FILE: str(path),
                FlextCliConstants.Cli.DictKeys.CONFIG_DATA: config_model,
                FlextCliConstants.Cli.DictKeys.MESSAGE: FlextCliConstants.Cli.ServiceMessages.CONFIG_LOADED_SUCCESSFULLY,
            })

            self.logger.info(
                FlextCliConstants.Cli.CmdMessages.CONFIG_EDIT_COMPLETED_LOG,
                config=config_info_str,
            )

            return r[str].ok(
                FlextCliConstants.Cli.LogMessages.CONFIG_EDIT_COMPLETED,
            )
        except Exception as e:
            return r[str].fail(
                FlextCliConstants.Cli.ErrorMessages.EDIT_CONFIG_FAILED.format(error=e),
            )


__all__ = [
    "FlextCliCmd",
]
