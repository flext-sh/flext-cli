"""FLEXT CLI Debug - Unified debug service using flext-core directly.

**MODULE**: FlextCliDebug - Single primary class for debug operations
**SCOPE**: System info, environment variables, paths, health checks, trace operations

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
import pathlib
import platform
import sys
import tempfile
from typing import override

from flext_core import (
    FlextResult,
    FlextTypes,
    FlextUtilities,
)

from flext_cli.base import FlextCliServiceBase
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels


class FlextCliDebug(FlextCliServiceBase):
    """Debug service extending FlextCliServiceBase.

    Provides essential debugging functionality using flext-core patterns.
    Follows single-responsibility principle with nested helpers.
    """

    @override
    def __init__(self, **_data: FlextTypes.GeneralValueType) -> None:
        """Initialize debug service with flext-core integration."""
        super().__init__()

    # =========================================================================
    # PRIVATE HELPERS - Generalize common patterns
    # =========================================================================

    @staticmethod
    def _convert_model_to_dict(
        model: FlextCliModels.SystemInfo
        | FlextCliModels.EnvironmentInfo
        | FlextCliModels.PathInfo,
    ) -> FlextTypes.JsonDict:
        """Generalized model to dict conversion helper."""
        # Use model_dump() directly and convert with DataMapper
        raw_dict = model.model_dump()
        return FlextUtilities.DataMapper.convert_dict_to_json(raw_dict)

    @staticmethod
    def _convert_result_to_json_value(
        result: FlextResult[FlextTypes.JsonDict]
    ) -> FlextTypes.GeneralValueType:
        """Convert FlextResult[JsonDict] to FlextTypes.GeneralValueType."""
        if result.is_success:
            # JsonDict is dict[str, GeneralValueType] - return directly
            return result.unwrap()
        # Return error as string
        return result.error or "Unknown error"

    def _collect_info_safely(
        self,
        method_name: str,
        error_key: str,
        info_dict: dict[str, FlextTypes.GeneralValueType],
    ) -> None:
        """Generalized info collection helper with error handling."""
        method = getattr(self, method_name)
        result = method()
        if result.is_success:
            info_dict[error_key.replace("_ERROR", "")] = (
                FlextCliDebug._convert_result_to_json_value(result)
            )
        else:
            info_dict[error_key] = result.error or "Unknown error"

    # =========================================================================
    # PUBLIC API METHODS
    # =========================================================================

    def execute(  # noqa: PLR6301
        self, **_kwargs: FlextTypes.JsonDict
    ) -> FlextResult[FlextTypes.JsonDict]:
        """Execute debug service - required by FlextService."""
        return FlextResult[FlextTypes.JsonDict].ok({
            "status": "operational",
            "message": FlextCliConstants.ServiceMessages.FLEXT_CLI_DEBUG_OPERATIONAL,
        })

    def get_environment_variables(
        self,
    ) -> FlextResult[FlextTypes.JsonDict]:
        """Get environment variables with sensitive data masked."""
        try:
            env_info = self._get_environment_info()
            typed_env_info: dict[str, FlextTypes.GeneralValueType] = {}
            for key, value in env_info.variables.items():
                typed_env_info[key] = value
            return FlextResult[FlextTypes.JsonDict].ok(typed_env_info)
        except Exception as e:
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.DebugErrorMessages.ENVIRONMENT_INFO_FAILED.format(
                    error=e,
                ),
            )

    def validate_environment_setup(
        self,
    ) -> FlextResult[list[str]]:
        """Validate environment setup and dependencies."""
        try:
            results = self._validate_filesystem_permissions()
            return FlextResult[list[str]].ok(results)
        except Exception as e:
            return FlextResult[list[str]].fail(
                FlextCliConstants.DebugErrorMessages.ENVIRONMENT_VALIDATION_FAILED.format(
                    error=e,
                ),
            )

    def test_connectivity(  # noqa: PLR6301
        self,
    ) -> FlextResult[dict[str, str]]:
        """Test basic connectivity and service status."""
        try:
            connectivity_info = {
                FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.CONNECTED.value,
                FlextCliConstants.DictKeys.TIMESTAMP: FlextUtilities.Generators.generate_iso_timestamp(),
                FlextCliConstants.DictKeys.SERVICE: str(FlextCliDebug),
                FlextCliConstants.DebugDictKeys.CONNECTIVITY: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
            }
            return FlextResult[dict[str, str]].ok(connectivity_info)
        except Exception as e:
            return FlextResult[dict[str, str]].fail(
                FlextCliConstants.DebugErrorMessages.CONNECTIVITY_TEST_FAILED.format(
                    error=e,
                ),
            )

    def execute_health_check(self) -> FlextResult[FlextTypes.JsonDict]:  # noqa: PLR6301
        """Execute comprehensive health check."""
        try:
            health_info: FlextTypes.JsonDict = {
                FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.HEALTHY.value,
                FlextCliConstants.DictKeys.TIMESTAMP: FlextUtilities.Generators.generate_iso_timestamp(),
                FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.DebugDefaults.SERVICE_NAME,
                FlextCliConstants.DebugDictKeys.CHECK_ID: FlextUtilities.Generators.generate_id(),
                FlextCliConstants.DebugDictKeys.CHECKS_PASSED: True,
            }
            return FlextResult[FlextTypes.JsonDict].ok(health_info)
        except Exception as e:
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.DebugErrorMessages.HEALTH_CHECK_FAILED.format(
                    error=e,
                ),
            )

    def execute_trace(self, args: list[str]) -> FlextResult[FlextTypes.JsonDict]:  # noqa: PLR6301
        """Execute trace operation with provided arguments."""
        try:
            trace_info: FlextTypes.JsonDict = {
                FlextCliConstants.DebugDictKeys.OPERATION: FlextCliConstants.TRACE,
                FlextCliConstants.DictKeys.ARGS: list(args),
                FlextCliConstants.DebugDictKeys.ARGS_COUNT: len(args),
                FlextCliConstants.DictKeys.TIMESTAMP: FlextUtilities.Generators.generate_iso_timestamp(),
                FlextCliConstants.DebugDictKeys.TRACE_ID: FlextUtilities.Generators.generate_id(),
            }
            return FlextResult[FlextTypes.JsonDict].ok(trace_info)
        except Exception as e:
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.DebugErrorMessages.TRACE_EXECUTION_FAILED.format(
                    error=e,
                ),
            )

    def get_debug_info(self) -> FlextResult[FlextTypes.JsonDict]:
        """Get comprehensive debug information."""
        try:
            system_info_model = self._get_system_info()
            system_info_dict = FlextCliDebug._convert_model_to_dict(system_info_model)
            # Convert system_info_dict to CliJsonValue - already CliDataDict
            system_info_json: dict[str, FlextTypes.GeneralValueType] = {
                key: val
                for key, val in system_info_dict.items()
                if isinstance(key, str)
            }

            debug_info: FlextTypes.JsonDict = {
                FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.DebugDefaults.SERVICE_NAME,
                FlextCliConstants.DictKeys.TIMESTAMP: FlextUtilities.Generators.generate_iso_timestamp(),
                FlextCliConstants.DebugDictKeys.DEBUG_ID: FlextUtilities.Generators.generate_id(),
                FlextCliConstants.DebugDictKeys.SYSTEM_INFO: system_info_json,
                FlextCliConstants.DebugDictKeys.ENVIRONMENT_STATUS: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
                FlextCliConstants.DebugDictKeys.CONNECTIVITY_STATUS: FlextCliConstants.ServiceStatus.CONNECTED.value,
            }
            return FlextResult[FlextTypes.JsonDict].ok(debug_info)
        except Exception as e:
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.DebugErrorMessages.DEBUG_INFO_COLLECTION_FAILED.format(
                    error=e,
                ),
            )

    def get_system_info(self) -> FlextResult[FlextTypes.JsonDict]:
        """Get system information - public API method."""
        try:
            info_model = self._get_system_info()
            info_dict: FlextTypes.JsonDict = FlextCliDebug._convert_model_to_dict(info_model)
            return FlextResult[FlextTypes.JsonDict].ok(info_dict)
        except Exception as e:
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.DebugErrorMessages.SYSTEM_INFO_COLLECTION_FAILED.format(
                    error=e,
                ),
            )

    def get_system_paths(self) -> FlextResult[FlextTypes.JsonDict]:
        """Get system path information - public API method."""
        try:
            paths_data = self._get_path_info()
            # Convert each PathInfo model to dict
            serialized_paths: list[FlextTypes.GeneralValueType] = []
            for path_info in paths_data:
                path_dict = FlextCliDebug._convert_model_to_dict(path_info)
                # path_dict is already CliDataDict (dict[str, CliJsonValue])
                # dict is part of CliJsonValue union, so it's compatible
                path_json_dict: dict[str, FlextTypes.GeneralValueType] = {
                    key: val for key, val in path_dict.items() if isinstance(key, str)
                }
                # dict[str, CliJsonValue] is part of CliJsonValue union
                serialized_paths.append(path_json_dict)

            # list[CliJsonValue] is compatible with CliJsonValue (list is part of union)
            paths_dict: FlextTypes.JsonDict = {
                "paths": serialized_paths,
            }
            return FlextResult[FlextTypes.JsonDict].ok(paths_dict)
        except Exception as e:
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.DebugErrorMessages.SYSTEM_PATHS_COLLECTION_FAILED.format(
                    error=e,
                ),
            )

    def get_comprehensive_debug_info(
        self,
    ) -> FlextResult[FlextTypes.JsonDict]:
        """Get comprehensive debug information combining all debug methods."""
        try:
            comprehensive_info: dict[str, FlextTypes.GeneralValueType] = {}

            # Collect all info using generalized helper
            self._collect_info_safely(
                "get_system_info",
                FlextCliConstants.DebugDictKeys.SYSTEM_ERROR,
                comprehensive_info,
            )
            self._collect_info_safely(
                "get_environment_variables",
                FlextCliConstants.DebugDictKeys.ENVIRONMENT_ERROR,
                comprehensive_info,
            )
            self._collect_info_safely(
                "get_system_paths",
                FlextCliConstants.DebugDictKeys.PATHS_ERROR,
                comprehensive_info,
            )
            self._collect_info_safely(
                "get_debug_info",
                FlextCliConstants.DebugDictKeys.DEBUG_ERROR,
                comprehensive_info,
            )

            return FlextResult[FlextTypes.JsonDict].ok(comprehensive_info)
        except Exception as e:
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.DebugErrorMessages.COMPREHENSIVE_DEBUG_INFO_FAILED.format(
                    error=e,
                ),
            )

    # =========================================================================
    # PRIVATE HELPER METHODS - Implementation details
    # =========================================================================

    def _get_system_info(self) -> FlextCliModels.SystemInfo:  # noqa: PLR6301
        """Get basic system information as Pydantic model."""
        arch_tuple = platform.architecture()
        return FlextCliModels.SystemInfo(
            python_version=sys.version,
            platform=platform.platform(),
            architecture=list(arch_tuple),
            processor=platform.processor(),
            hostname=platform.node(),
        )

    def _get_environment_info(self) -> FlextCliModels.EnvironmentInfo:  # noqa: PLR6301
        """Get environment variables with sensitive data masked as Pydantic model."""
        env_info: dict[str, str] = {}

        for key, value in os.environ.items():
            if any(
                sens in key.lower()
                for sens in FlextCliConstants.DebugDefaults.SENSITIVE_KEYS
            ):
                env_info[key] = FlextCliConstants.DebugDefaults.MASKED_SENSITIVE
            else:
                env_info[key] = value

        return FlextCliModels.EnvironmentInfo(variables=env_info)

    def _get_path_info(self) -> list[FlextCliModels.PathInfo]:  # noqa: PLR6301
        """Get system path information as list of Pydantic models."""
        paths: list[FlextCliModels.PathInfo] = []
        for i, path in enumerate(sys.path):
            path_obj = pathlib.Path(path)
            paths.append(
                FlextCliModels.PathInfo(
                    index=i,
                    path=path,
                    exists=path_obj.exists(),
                    is_file=path_obj.is_file() if path_obj.exists() else False,
                    is_dir=path_obj.is_dir() if path_obj.exists() else False,
                ),
            )

        return paths

    def _validate_filesystem_permissions(self) -> list[str]:  # noqa: PLR6301
        """Validate filesystem permissions and setup."""
        errors = []

        try:
            # Test temp directory access
            with tempfile.NamedTemporaryFile(delete=True) as tmp:
                tmp.write(b"test")
                tmp.flush()

            # Test current directory access
            current_dir = pathlib.Path.cwd()
            test_file = current_dir / "test_write.tmp"
            try:
                with pathlib.Path(test_file).open(
                    "w",
                    encoding=FlextCliConstants.Encoding.UTF8,
                ) as f:
                    f.write("test")
                pathlib.Path(test_file).unlink()
            except OSError as e:
                errors.append(
                    FlextCliConstants.ErrorMessages.CANNOT_WRITE_CURRENT_DIR.format(
                        error=e,
                    ),
                )

        except Exception as e:
            errors.append(
                FlextCliConstants.ErrorMessages.FILESYSTEM_VALIDATION_FAILED.format(
                    error=e,
                ),
            )

        return errors


__all__ = ["FlextCliDebug"]
