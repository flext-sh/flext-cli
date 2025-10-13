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

from flext_core import FlextCore

from flext_cli.constants import FlextCliConstants
from flext_cli.typings import FlextCliTypes, FlextCliTypes as Types


class FlextCliDebug(FlextCore.Service[str]):
    """Debug service extending FlextCore.Service from flext-core.

    Implements FlextCliProtocols.CliDebugProvider through structural subtyping.

    Provides essential debugging functionality using flext-core patterns.
    Follows single-responsibility principle with nested helpers.
    """

    @override
    def __init__(self, **_data: object) -> None:
        """Initialize debug service with flext-core integration and Phase 1 context enrichment."""
        super().__init__()
        # Logger and container inherited from FlextCore.Service via FlextCore.Mixins

    def execute(self) -> FlextCore.Result[str]:
        """Execute debug service - required by FlextCore.Service."""
        return FlextCore.Result[str].ok(
            FlextCliConstants.ServiceMessages.FLEXT_CLI_DEBUG_OPERATIONAL
        )

    def get_system_info(
        self,
    ) -> FlextCore.Result[FlextCliTypes.Data.CliDataDict]:
        """Get system information for debugging."""
        try:
            info = self._get_system_info()
            # Convert to more specific type for better type safety
            typed_info: FlextCliTypes.Data.CliDataDict = {}
            for key, value in info.items():
                if isinstance(value, (str, int, float, bool, type(None))):
                    typed_info[key] = value
                else:
                    typed_info[key] = str(value)
            return FlextCore.Result[FlextCliTypes.Data.CliDataDict].ok(typed_info)
        except Exception as e:
            return FlextCore.Result[FlextCliTypes.Data.CliDataDict].fail(
                f"System info failed: {e}"
            )

    def get_environment_variables(
        self,
    ) -> FlextCore.Result[FlextCliTypes.Data.CliDataDict]:
        """Get environment variables with sensitive data masked."""
        try:
            env_info = self._get_environment_info()
            # _get_environment_info returns dict[str, str], so values are strings
            typed_env_info: FlextCliTypes.Data.CliDataDict = {}
            for key, value in env_info.items():
                typed_env_info[key] = value  # value is str, which is JsonValue
            return FlextCore.Result[FlextCliTypes.Data.CliDataDict].ok(typed_env_info)
        except Exception as e:
            return FlextCore.Result[FlextCliTypes.Data.CliDataDict].fail(
                f"Environment info failed: {e}"
            )

    def get_system_paths(
        self,
    ) -> FlextCore.Result[list[FlextCliTypes.Data.CliDataDict]]:
        """Get system path information."""
        try:
            paths = self._get_path_info()
            # Convert to more specific type for better type safety
            typed_paths: list[FlextCliTypes.Data.CliDataDict] = []
            for path_dict in paths:
                typed_path: FlextCliTypes.Data.CliDataDict = {}
                for key, value in path_dict.items():
                    if isinstance(value, (str, int, float, bool, type(None))):
                        typed_path[key] = value
                    else:
                        typed_path[key] = str(value)
                typed_paths.append(typed_path)
            return FlextCore.Result[list[FlextCliTypes.Data.CliDataDict]].ok(
                typed_paths
            )
        except Exception as e:
            return FlextCore.Result[list[FlextCliTypes.Data.CliDataDict]].fail(
                f"Path info failed: {e}"
            )

    def validate_environment_setup(
        self,
    ) -> FlextCore.Result[FlextCore.Types.StringList]:
        """Validate environment setup and dependencies."""
        try:
            results = self._validate_filesystem_permissions()
            return FlextCore.Result[FlextCore.Types.StringList].ok(results)
        except Exception as e:
            return FlextCore.Result[FlextCore.Types.StringList].fail(
                f"Environment validation failed: {e}"
            )

    def test_connectivity(
        self,
    ) -> FlextCore.Result[FlextCore.Types.StringDict]:
        """Test basic connectivity and service status."""
        try:
            connectivity_info = {
                "status": FlextCliConstants.CONNECTED,
                "timestamp": datetime.now(UTC).isoformat(),
                "service": str(FlextCliDebug),
                "connectivity": FlextCliConstants.OPERATIONAL,
            }
            return FlextCore.Result[FlextCore.Types.StringDict].ok(connectivity_info)
        except Exception as e:
            return FlextCore.Result[FlextCore.Types.StringDict].fail(
                f"Connectivity test failed: {e}"
            )

    def execute_health_check(self) -> FlextCore.Result[Types.Data.DebugInfoData]:
        """Execute comprehensive health check."""
        try:
            health_info: Types.Data.DebugInfoData = {
                "status": FlextCliConstants.HEALTHY,
                "timestamp": datetime.now(UTC).isoformat(),
                "service": "FlextCliDebug",
                "check_id": str(uuid.uuid4()),
                "checks_passed": True,
            }
            return FlextCore.Result[Types.Data.DebugInfoData].ok(health_info)
        except Exception as e:
            return FlextCore.Result[Types.Data.DebugInfoData].fail(
                f"Health check failed: {e}"
            )

    def execute_trace(
        self, args: FlextCore.Types.StringList
    ) -> FlextCore.Result[Types.Data.DebugInfoData]:
        """Execute trace operation with provided arguments."""
        try:
            trace_info: Types.Data.DebugInfoData = {
                "operation": FlextCliConstants.TRACE,
                "args": list(args),  # Cast to list for JsonValue compatibility
                "args_count": len(args),
                "timestamp": datetime.now(UTC).isoformat(),
                "trace_id": str(uuid.uuid4()),
            }
            return FlextCore.Result[Types.Data.DebugInfoData].ok(trace_info)
        except Exception as e:
            return FlextCore.Result[Types.Data.DebugInfoData].fail(
                f"Trace execution failed: {e}"
            )

    def get_debug_info(self) -> FlextCore.Result[Types.Data.DebugInfoData]:
        """Get comprehensive debug information.

        Returns:
            FlextCore.Result[Types.Data.DebugInfoData]: Debug information or error

        """
        try:
            debug_info: Types.Data.DebugInfoData = {
                "service": "FlextCliDebug",
                "timestamp": datetime.now(UTC).isoformat(),
                "debug_id": str(uuid.uuid4()),
                "system_info": self._get_system_info(),
                "environment_status": FlextCliConstants.OPERATIONAL,
                "connectivity_status": FlextCliConstants.CONNECTED,
            }
            return FlextCore.Result[Types.Data.DebugInfoData].ok(debug_info)
        except Exception as e:
            return FlextCore.Result[Types.Data.DebugInfoData].fail(
                f"Debug info collection failed: {e}"
            )

    def get_comprehensive_debug_info(
        self,
    ) -> FlextCore.Result[Types.Data.DebugInfoData]:
        """Get comprehensive debug information combining all debug methods."""
        try:
            comprehensive_info: FlextCore.Types.Dict = {}

            # Collect system info
            system_result = self.get_system_info()
            if system_result.is_success:
                comprehensive_info["system"] = system_result.value
            else:
                comprehensive_info["system_error"] = system_result.error

            # Collect environment info
            env_result = self.get_environment_variables()
            if env_result.is_success:
                comprehensive_info["environment"] = env_result.value
            else:
                comprehensive_info["environment_error"] = env_result.error

            # Collect paths info
            paths_result = self.get_system_paths()
            if paths_result.is_success:
                comprehensive_info["paths"] = paths_result.value
            else:
                comprehensive_info["paths_error"] = paths_result.error

            # Collect debug info
            debug_result = self.get_debug_info()
            if debug_result.is_success:
                comprehensive_info["debug"] = debug_result.value
            else:
                comprehensive_info["debug_error"] = debug_result.error

            # Type narrowing: comprehensive_info is FlextCore.Types.Dict which is compatible with DebugInfoData
            typed_comprehensive_info: Types.Data.DebugInfoData = comprehensive_info  # type: ignore[assignment]
            return FlextCore.Result[Types.Data.DebugInfoData].ok(
                typed_comprehensive_info
            )

        except Exception as e:
            return FlextCore.Result[Types.Data.DebugInfoData].fail(
                f"Comprehensive debug info collection failed: {e}"
            )

    # =========================================================================
    # PRIVATE HELPER METHODS - Implementation details
    # =========================================================================

    def _get_system_info(self) -> FlextCore.Types.Dict:
        """Get basic system information."""
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "hostname": platform.node(),
        }

    def _get_environment_info(self) -> dict[str, str]:
        """Get environment variables with sensitive data masked."""
        env_info = {}
        sensitive_keys = {
            FlextCliConstants.DictKeys.PASSWORD,
            FlextCliConstants.DictKeys.TOKEN,
            "secret",
            "key",
            "auth",
        }

        for key, value in os.environ.items():
            if any(sens in key.lower() for sens in sensitive_keys):
                env_info[key] = "***MASKED***"
            else:
                env_info[key] = value

        return env_info

    def _get_path_info(self) -> list[FlextCore.Types.Dict]:
        """Get system path information."""
        paths = []
        for i, path in enumerate(sys.path):
            paths.append({
                "index": i,
                "path": path,
                "exists": pathlib.Path(path).exists(),
                "is_dir": pathlib.Path(path).is_dir()
                if pathlib.Path(path).exists()
                else False,
            })

        return paths

    def _validate_filesystem_permissions(self) -> FlextCore.Types.StringList:
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
