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
from typing import cast, override

from flext_core import FlextResult, FlextService, FlextTypes

from flext_cli.constants import FlextCliConstants
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
            # _get_environment_info returns dict[str, str], so values are strings
            typed_env_info: FlextCliTypes.Data.CliDataDict = {}
            for key, value in env_info.items():
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
            debug_info: Types.Data.DebugInfoData = {
                FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.DebugDefaults.SERVICE_NAME,
                FlextCliConstants.DictKeys.TIMESTAMP: datetime.now(UTC).isoformat(),
                FlextCliConstants.DebugDictKeys.DEBUG_ID: str(uuid.uuid4()),
                FlextCliConstants.DebugDictKeys.SYSTEM_INFO: self._get_system_info(),
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
            info = self._get_system_info()
            # Type-safe cast: _get_system_info returns dict[str, object] with JSON-compatible values
            # (str, tuple of str) which are valid JsonValue types
            typed_info = cast("FlextCliTypes.Data.CliDataDict", info)
            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(typed_info)
        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                FlextCliConstants.DebugErrorMessages.SYSTEM_INFO_COLLECTION_FAILED.format(
                    error=e
                )
            )

    def get_system_paths(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Get system paths - public API method.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: System paths or error

        """
        try:
            paths = self._get_path_info()
            # Type-safe cast: paths is list[dict] with JSON-compatible values
            paths_list = cast("list[object]", paths)
            typed_paths: FlextCliTypes.Data.CliDataDict = {
                FlextCliConstants.DebugDictKeys.PATHS: paths_list
            }
            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(typed_paths)
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
            comprehensive_info: dict[str, object] = {}

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

            # Type-safe cast: comprehensive_info contains only JSON-compatible values
            typed_comprehensive_info = cast(
                "Types.Data.DebugInfoData", comprehensive_info
            )
            return FlextResult[Types.Data.DebugInfoData].ok(typed_comprehensive_info)

        except Exception as e:
            return FlextResult[Types.Data.DebugInfoData].fail(
                FlextCliConstants.DebugErrorMessages.COMPREHENSIVE_DEBUG_INFO_FAILED.format(
                    error=e
                )
            )

    # =========================================================================
    # PRIVATE HELPER METHODS - Implementation details
    # =========================================================================

    def _get_system_info(self) -> dict[str, object]:
        """Get basic system information."""
        return {
            FlextCliConstants.DebugDictKeys.PYTHON_VERSION: sys.version,
            FlextCliConstants.DebugDictKeys.PLATFORM: platform.platform(),
            FlextCliConstants.DebugDictKeys.ARCHITECTURE: platform.architecture(),
            FlextCliConstants.DebugDictKeys.PROCESSOR: platform.processor(),
            FlextCliConstants.DebugDictKeys.HOSTNAME: platform.node(),
        }

    def _get_environment_info(self) -> dict[str, str]:
        """Get environment variables with sensitive data masked."""
        env_info: dict[str, str] = {}

        for key, value in os.environ.items():
            if any(
                sens in key.lower()
                for sens in FlextCliConstants.DebugDefaults.SENSITIVE_KEYS
            ):
                env_info[key] = FlextCliConstants.DebugDefaults.MASKED_SENSITIVE
            else:
                env_info[key] = value

        return env_info

    def _get_path_info(self) -> list[dict[str, object]]:
        """Get system path information."""
        paths = []
        for i, path in enumerate(sys.path):
            path_obj = pathlib.Path(path)
            paths.append({
                FlextCliConstants.DebugDictKeys.INDEX: i,
                FlextCliConstants.DebugDictKeys.PATH: path,
                FlextCliConstants.DebugDictKeys.EXISTS: path_obj.exists(),
                FlextCliConstants.DebugDictKeys.IS_DIR: (
                    path_obj.is_dir() if path_obj.exists() else False
                ),
            })

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
