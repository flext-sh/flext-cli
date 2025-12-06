"""Command execution and configuration bridge for flext-cli.

Encapsula a ponte entre comandos registrados, utilidades de arquivo e helpers de
configuração usando `FlextResult` para sucesso/falha previsível.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path
from typing import override

from flext_core import r

from flext_cli.base import FlextCliServiceBase
from flext_cli.constants import c
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.models import m
from flext_cli.services.output import FlextCliOutput
from flext_cli.typings import t
from flext_cli.utilities import u


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
    7. Config operations MUST delegate to u.ConfigOps
    8. Command execution MUST log all operations for audit trail

    Architecture Implications:
    ───────────────────────────
    - Extends FlextCliServiceBase for consistent logging and container access
    - Delegates file operations to FlextCliFileTools (SRP)
    - Delegates config operations to u.ConfigOps (SRP)
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
    # All config utilities moved to u.ConfigOps
    """

    @override
    def __init__(self) -> None:
        """Initialize the command service and supporting file helpers."""
        super().__init__()
        # Logger is automatically provided by FlextMixins mixin
        self._file_tools = FlextCliFileTools()

    def execute(self, **_kwargs: t.Json.JsonDict) -> r[t.Json.JsonDict]:
        """Report operational status required by `FlextService`."""
        return r[t.Json.JsonDict].ok({
            c.DictKeys.STATUS: c.ServiceStatus.OPERATIONAL.value,
            c.DictKeys.SERVICE: c.CmdDefaults.SERVICE_NAME,
        })

    @staticmethod
    def show_config_paths() -> r[list[str]]:
        """Show configuration paths using FlextCliUtilities directly."""
        try:
            paths = u.ConfigOps.get_config_paths()
            return r[list[str]].ok(paths)
        except Exception as e:
            return r[list[str]].fail(
                c.ErrorMessages.CONFIG_PATHS_FAILED.format(error=e),
            )

    def validate_config(self) -> r[bool]:
        """Validate configuration structure using FlextCliUtilities directly.

        Returns:
            r[bool]: True if validation passed, or error

        """
        try:
            results = u.ConfigOps.validate_config_structure()
            if results:
                self.logger.info(
                    c.LogMessages.CONFIG_VALIDATION_RESULTS.format(
                        results=results,
                    ),
                )
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(
                c.ErrorMessages.CONFIG_VALIDATION_FAILED.format(
                    error=e,
                ),
            )

    @staticmethod
    def get_config_info() -> r[t.Json.JsonDict]:
        """Get configuration information using FlextCliUtilities directly."""
        try:
            info = u.ConfigOps.get_config_info()
            return r[t.Json.JsonDict].ok(info)
        except Exception as e:
            return r[t.Json.JsonDict].fail(
                c.ErrorMessages.CONFIG_INFO_FAILED.format(error=e),
            )

    def set_config_value(self, key: str, value: str) -> r[bool]:
        """Set configuration value with real persistence using flext-core."""
        try:
            config_path = (
                FlextCliServiceBase.get_cli_config().config_dir
                / c.ConfigFiles.CLI_CONFIG_JSON
            )
            config_data: t.GeneralValueType = {key: value}
            save_result = self._file_tools.write_json_file(
                file_path=str(config_path),
                data=config_data,
            )

            if save_result.is_failure:
                return r[bool].fail(
                    c.CmdErrorMessages.CONFIG_SAVE_FAILED.format(
                        error=save_result.error,
                    ),
                )

            self.logger.info(
                c.CmdMessages.CONFIG_SAVED.format(key=key, value=value),
            )
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(
                c.ErrorMessages.SET_CONFIG_FAILED.format(error=e),
            )

    def get_config_value(self, key: str) -> r[t.Json.JsonDict]:
        """Get configuration value with real persistence using flext-core."""
        try:
            config_path = (
                FlextCliServiceBase.get_cli_config().config_dir
                / c.ConfigFiles.CLI_CONFIG_JSON
            )

            if not config_path.exists():
                return r[t.Json.JsonDict].fail(
                    c.CmdErrorMessages.CONFIG_FILE_NOT_FOUND.format(
                        path=config_path,
                    ),
                )

            load_result = self._file_tools.read_json_file(str(config_path))
            if load_result.is_failure:
                return r[t.Json.JsonDict].fail(
                    c.CmdErrorMessages.CONFIG_LOAD_FAILED.format(
                        error=load_result.error,
                    ),
                )

            config_data = load_result.value
            if not isinstance(config_data, dict):
                return r[t.Json.JsonDict].fail(
                    c.CmdErrorMessages.CONFIG_NOT_DICT,
                )

            if key not in config_data:
                return r[t.Json.JsonDict].fail(
                    c.CmdErrorMessages.CONFIG_KEY_NOT_FOUND.format(
                        key=key,
                    ),
                )

            value = config_data[key]
            # Use u.transform for JSON conversion
            raw_data = {
                c.DictKeys.KEY: key,
                c.DictKeys.VALUE: value,
                c.DictKeys.TIMESTAMP: u.generate("timestamp"),
            }
            # Use build() DSL for JSON conversion
            # Reuse to_dict_json helper from output module
            result_data_raw = FlextCliOutput.cast_if(
                FlextCliOutput.to_dict_json(raw_data),
                dict,
                raw_data,
            )
            result_data: t.Json.JsonDict = (
                result_data_raw if isinstance(result_data_raw, dict) else {}
            )
            return r[t.Json.JsonDict].ok(result_data)
        except Exception as e:
            return r[t.Json.JsonDict].fail(
                c.CmdErrorMessages.GET_CONFIG_FAILED.format(error=e),
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
                    c.CmdErrorMessages.SHOW_CONFIG_FAILED.format(
                        error=info_result.error,
                    ),
                )

            self.logger.info(
                c.LogMessages.CONFIG_DISPLAYED,
                config=info_result.value,
            )
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(
                c.CmdErrorMessages.SHOW_CONFIG_FAILED.format(error=e),
            )

    def edit_config(self) -> r[str]:
        """Edit configuration using Pydantic validation - no wrappers."""
        try:
            config_path = (
                FlextCliServiceBase.get_cli_config().config_dir
                / c.ConfigFiles.CLI_CONFIG_JSON
            )
            path = Path(str(config_path))

            if not path.exists():
                default_config_model = m.CmdConfig(name="default")
                save_result = self._file_tools.write_json_file(
                    file_path=str(path),
                    data=default_config_model.model_dump(),
                )
                if save_result.is_failure:
                    return r[str].fail(
                        c.CmdErrorMessages.CREATE_DEFAULT_CONFIG_FAILED.format(
                            error=save_result.error,
                        ),
                    )

            load_result = self._file_tools.read_json_file(str(path))
            if load_result.is_failure:
                return r[str].fail(
                    c.CmdErrorMessages.CONFIG_LOAD_FAILED.format(
                        error=load_result.error,
                    ),
                )

            try:
                config_model = m.CmdConfig.model_validate(
                    load_result.value,
                )
            except Exception:
                return r[str].fail(
                    c.CmdErrorMessages.CONFIG_NOT_DICT,
                )

            config_data = config_model.model_dump()
            config_info_str = str({
                c.DictKeys.CONFIG_FILE: str(path),
                c.DictKeys.CONFIG_DATA: config_data,
                c.DictKeys.MESSAGE: c.ServiceMessages.CONFIG_LOADED_SUCCESSFULLY,
            })

            self.logger.info(
                c.CmdMessages.CONFIG_EDIT_COMPLETED_LOG,
                config=config_info_str,
            )

            return r[str].ok(
                c.LogMessages.CONFIG_EDIT_COMPLETED,
            )
        except Exception as e:
            return r[str].fail(
                c.ErrorMessages.EDIT_CONFIG_FAILED.format(error=e),
            )


__all__ = [
    "FlextCliCmd",
]
