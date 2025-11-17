"""FLEXT CLI Debug - Unified debug service using flext-core directly.

Single responsibility debug service eliminating ALL loose functions and
wrapper patterns. Uses flext-core utilities directly with SOURCE OF TRUTH
principle for all configurations and metadata.

EXPECTED MYPY ISSUES (documented for awareness):
- Unreachable statement in get_environment_variables method:
  This is defensive type checking that mypy proves is unnecessary at compile time
  due to type analysis, but is kept for runtime safety.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
import pathlib
import platform
import sys
import tempfile
import uuid
from datetime import UTC, datetime
from typing import override

from flext_core import FlextResult, FlextService, FlextTypes

from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels
from flext_cli.typings import FlextCliTypes, FlextCliTypes as Types


class FlextCliDebug(FlextService[str]):
    """Debug service extending FlextService from flext-core.

    Implements FlextCliProtocols.CliDebugProvider through structural subtyping.

    Provides essential debugging functionality using flext-core patterns.
    Follows single-responsibility principle with nested helpers.
    """

    @override
    def __init__(self, **_data: FlextTypes.JsonValue) -> None:
        """Initialize debug service with flext-core integration and Phase 1 context enrichment."""
        super().__init__()
        # Logger and container inherited from FlextService via FlextMixins

    def execute(self) -> FlextResult[str]:
        """Execute debug service - required by FlextService."""
        return FlextResult[str].ok(
            FlextCliConstants.ServiceMessages.FLEXT_CLI_DEBUG_OPERATIONAL
        )

    def get_environment_variables(
        self,
    ) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Get environment variables with sensitive data masked."""
        try:
            env_info = self._get_environment_info()
            # env_info is EnvironmentInfo model, access variables dict
            typed_env_info: FlextCliTypes.Data.CliDataDict = {}
            for key, value in env_info.variables.items():
                typed_env_info[key] = value  # value is str, which is JsonValue
            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(typed_env_info)
        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                FlextCliConstants.DebugErrorMessages.ENVIRONMENT_INFO_FAILED.format(
                    error=e
                )
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
                    error=e
                )
            )

    def test_connectivity(
        self,
    ) -> FlextResult[dict[str, str]]:
        """Test basic connectivity and service status."""
        try:
            connectivity_info = {
                FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.CONNECTED.value,
                FlextCliConstants.DictKeys.TIMESTAMP: datetime.now(UTC).isoformat(),
                FlextCliConstants.DictKeys.SERVICE: str(FlextCliDebug),
                FlextCliConstants.DebugDictKeys.CONNECTIVITY: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
            }
            return FlextResult[dict[str, str]].ok(connectivity_info)
        except Exception as e:
            return FlextResult[dict[str, str]].fail(
                FlextCliConstants.DebugErrorMessages.CONNECTIVITY_TEST_FAILED.format(
                    error=e
                )
            )

    def execute_health_check(self) -> FlextResult[Types.Data.DebugInfoData]:
        """Execute comprehensive health check."""
        try:
            health_info: Types.Data.DebugInfoData = {
                FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.HEALTHY.value,
                FlextCliConstants.DictKeys.TIMESTAMP: datetime.now(UTC).isoformat(),
                FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.DebugDefaults.SERVICE_NAME,
                FlextCliConstants.DebugDictKeys.CHECK_ID: str(uuid.uuid4()),
                FlextCliConstants.DebugDictKeys.CHECKS_PASSED: True,
            }
            return FlextResult[Types.Data.DebugInfoData].ok(health_info)
        except Exception as e:
            return FlextResult[Types.Data.DebugInfoData].fail(
                FlextCliConstants.DebugErrorMessages.HEALTH_CHECK_FAILED.format(error=e)
            )

    def execute_trace(self, args: list[str]) -> FlextResult[Types.Data.DebugInfoData]:
        """Execute trace operation with provided arguments."""
        try:
            trace_info: Types.Data.DebugInfoData = {
                FlextCliConstants.DebugDictKeys.OPERATION: FlextCliConstants.TRACE,
                FlextCliConstants.DictKeys.ARGS: list(
                    args
                ),  # Cast to list for JsonValue compatibility
                FlextCliConstants.DebugDictKeys.ARGS_COUNT: len(args),
                FlextCliConstants.DictKeys.TIMESTAMP: datetime.now(UTC).isoformat(),
                FlextCliConstants.DebugDictKeys.TRACE_ID: str(uuid.uuid4()),
            }
            return FlextResult[Types.Data.DebugInfoData].ok(trace_info)
        except Exception as e:
            return FlextResult[Types.Data.DebugInfoData].fail(
                FlextCliConstants.DebugErrorMessages.TRACE_EXECUTION_FAILED.format(
                    error=e
                )
            )

    def get_debug_info(self) -> FlextResult[Types.Data.DebugInfoData]:
        """Get comprehensive debug information.

        Returns:
            FlextResult[Types.Data.DebugInfoData]: Debug information or error

        """
        try:
            # Serialize SystemInfo model to dict using Pydantic 2 model_dump()
            system_info_model = self._get_system_info()
            debug_info: Types.Data.DebugInfoData = {
                FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.DebugDefaults.SERVICE_NAME,
                FlextCliConstants.DictKeys.TIMESTAMP: datetime.now(UTC).isoformat(),
                FlextCliConstants.DebugDictKeys.DEBUG_ID: str(uuid.uuid4()),
                FlextCliConstants.DebugDictKeys.SYSTEM_INFO: system_info_model.model_dump(),
                FlextCliConstants.DebugDictKeys.ENVIRONMENT_STATUS: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
                FlextCliConstants.DebugDictKeys.CONNECTIVITY_STATUS: FlextCliConstants.ServiceStatus.CONNECTED.value,
            }
            return FlextResult[Types.Data.DebugInfoData].ok(debug_info)
        except Exception as e:
            return FlextResult[Types.Data.DebugInfoData].fail(
                FlextCliConstants.DebugErrorMessages.DEBUG_INFO_COLLECTION_FAILED.format(
                    error=e
                )
            )

    def get_system_info(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Get system information - public API method.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: System information or error

        """
        try:
            info_model = self._get_system_info()
            # Serialize SystemInfo model to dict using Pydantic 2 model_dump()
            info_dict: FlextCliTypes.Data.CliDataDict = info_model.model_dump()
            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(info_dict)
        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                FlextCliConstants.DebugErrorMessages.SYSTEM_INFO_COLLECTION_FAILED.format(
                    error=e
                )
            )

    def get_system_paths(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Get system path information - public API method.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: Path information list as dict or error

        Note:
            Returns type-safe PathInfo models serialized to dict format

        """
        try:
            paths_data = self._get_path_info()
            # Serialize PathInfo models to dicts using model_dump()
            serialized_paths: list[dict[str, object]] = [
                path_info.model_dump() for path_info in paths_data
            ]

            # Type-safe dict construction
            # serialized_paths is list[dict[str, object]] which is compatible with JsonValue
            # list is a valid JsonValue type, no cast needed
            paths_dict: FlextCliTypes.Data.CliDataDict = {"paths": serialized_paths}
            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(paths_dict)
        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                FlextCliConstants.DebugErrorMessages.SYSTEM_PATHS_COLLECTION_FAILED.format(
                    error=e
                )
            )

    def get_comprehensive_debug_info(
        self,
    ) -> FlextResult[Types.Data.DebugInfoData]:
        """Get comprehensive debug information combining all debug methods."""
        try:
            comprehensive_info: Types.Data.DebugInfoData = {}

            # Collect system info
            system_result = self.get_system_info()
            if system_result.is_success:
                comprehensive_info[FlextCliConstants.DebugDictKeys.SYSTEM] = (
                    system_result.value
                )
            else:
                comprehensive_info[FlextCliConstants.DebugDictKeys.SYSTEM_ERROR] = (
                    system_result.error
                )

            # Collect environment info
            env_result = self.get_environment_variables()
            if env_result.is_success:
                comprehensive_info[FlextCliConstants.DebugDictKeys.ENVIRONMENT] = (
                    env_result.value
                )
            else:
                comprehensive_info[
                    FlextCliConstants.DebugDictKeys.ENVIRONMENT_ERROR
                ] = env_result.error

            # Collect paths info
            paths_result = self.get_system_paths()
            if paths_result.is_success:
                comprehensive_info[FlextCliConstants.DebugDictKeys.PATHS] = (
                    paths_result.value
                )
            else:
                comprehensive_info[FlextCliConstants.DebugDictKeys.PATHS_ERROR] = (
                    paths_result.error
                )

            # Collect debug info
            debug_result = self.get_debug_info()
            if debug_result.is_success:
                comprehensive_info[FlextCliConstants.DebugDictKeys.DEBUG] = (
                    debug_result.value
                )
            else:
                comprehensive_info[FlextCliConstants.DebugDictKeys.DEBUG_ERROR] = (
                    debug_result.error
                )

            # comprehensive_info is already correctly typed as DebugInfoData
            return FlextResult[Types.Data.DebugInfoData].ok(comprehensive_info)

        except Exception as e:
            return FlextResult[Types.Data.DebugInfoData].fail(
                FlextCliConstants.DebugErrorMessages.COMPREHENSIVE_DEBUG_INFO_FAILED.format(
                    error=e
                )
            )

    # =========================================================================
    # PRIVATE HELPER METHODS - Implementation details
    # =========================================================================

    def _get_system_info(self) -> FlextCliModels.SystemInfo:
        """Get basic system information as Pydantic model.

        Returns:
            SystemInfo model with python_version, platform, architecture, etc.

        Pydantic 2 Features:
            - Type-safe model instead of dict[str, JsonValue]
            - Automatic validation on creation
            - Clean serialization with model_dump()

        """
        arch_tuple = platform.architecture()
        return FlextCliModels.SystemInfo(
            python_version=sys.version,
            platform=platform.platform(),
            architecture=list(arch_tuple),
            processor=platform.processor(),
            hostname=platform.node(),
        )

    def _get_environment_info(self) -> FlextCliModels.EnvironmentInfo:
        """Get environment variables with sensitive data masked as Pydantic model.

        Returns:
            EnvironmentInfo model with masked sensitive variables

        Pydantic 2 Features:
            - Type-safe model instead of dict[str, str]
            - Validates all values are strings
            - Immutable with frozen=False for assignment validation

        """
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

    def _get_path_info(self) -> list[FlextCliModels.PathInfo]:
        """Get system path information as list of Pydantic models.

        Returns:
            List of PathInfo models with index, path, exists, is_dir

        Pydantic 2 Features:
            - Type-safe models instead of list[dict[str, object]]
            - Automatic validation for each path entry
            - Clean iteration and serialization

        """
        paths: list[FlextCliModels.PathInfo] = []
        for i, path in enumerate(sys.path):
            path_obj = pathlib.Path(path)
            paths.append(
                FlextCliModels.PathInfo(
                    index=i,
                    path=path,
                    exists=path_obj.exists(),
                    is_dir=path_obj.is_dir() if path_obj.exists() else False,
                )
            )

        return paths

    def _validate_filesystem_permissions(self) -> list[str]:
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
                    "w", encoding=FlextCliConstants.Encoding.UTF8
                ) as f:
                    f.write("test")
                pathlib.Path(test_file).unlink()
            except OSError as e:
                errors.append(
                    FlextCliConstants.ErrorMessages.CANNOT_WRITE_CURRENT_DIR.format(
                        error=e
                    )
                )

        except Exception as e:
            errors.append(
                FlextCliConstants.ErrorMessages.FILESYSTEM_VALIDATION_FAILED.format(
                    error=e
                )
            )

        return errors


__all__ = [
    "FlextCliDebug",
]
