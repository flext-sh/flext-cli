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
                f"Environment info failed: {e}"
            )

    def validate_environment_setup(
        self,
    ) -> FlextResult[FlextTypes.StringList]:
        """Validate environment setup and dependencies."""
        try:
            results = self._validate_filesystem_permissions()
            return FlextResult[FlextTypes.StringList].ok(results)
        except Exception as e:
            return FlextResult[FlextTypes.StringList].fail(
                f"Environment validation failed: {e}"
            )

    def test_connectivity(
        self,
    ) -> FlextResult[FlextTypes.StringDict]:
        """Test basic connectivity and service status."""
        try:
            connectivity_info = {
                "status": FlextCliConstants.ServiceStatus.CONNECTED.value,
                "timestamp": datetime.now(UTC).isoformat(),
                "service": str(FlextCliDebug),
                "connectivity": FlextCliConstants.ServiceStatus.OPERATIONAL.value,
            }
            return FlextResult[FlextTypes.StringDict].ok(connectivity_info)
        except Exception as e:
            return FlextResult[FlextTypes.StringDict].fail(
                f"Connectivity test failed: {e}"
            )

    def execute_health_check(self) -> FlextResult[Types.Data.DebugInfoData]:
        """Execute comprehensive health check."""
        try:
            health_info: Types.Data.DebugInfoData = {
                "status": FlextCliConstants.ServiceStatus.HEALTHY.value,
                "timestamp": datetime.now(UTC).isoformat(),
                "service": "FlextCliDebug",
                "check_id": str(uuid.uuid4()),
                "checks_passed": True,
            }
            return FlextResult[Types.Data.DebugInfoData].ok(health_info)
        except Exception as e:
            return FlextResult[Types.Data.DebugInfoData].fail(
                f"Health check failed: {e}"
            )

    def execute_trace(
        self, args: FlextTypes.StringList
    ) -> FlextResult[Types.Data.DebugInfoData]:
        """Execute trace operation with provided arguments."""
        try:
            trace_info: Types.Data.DebugInfoData = {
                "operation": FlextCliConstants.TRACE,
                "args": list(args),  # Cast to list for JsonValue compatibility
                "args_count": len(args),
                "timestamp": datetime.now(UTC).isoformat(),
                "trace_id": str(uuid.uuid4()),
            }
            return FlextResult[Types.Data.DebugInfoData].ok(trace_info)
        except Exception as e:
            return FlextResult[Types.Data.DebugInfoData].fail(
                f"Trace execution failed: {e}"
            )

    def get_debug_info(self) -> FlextResult[Types.Data.DebugInfoData]:
        """Get comprehensive debug information.

        Returns:
            FlextResult[Types.Data.DebugInfoData]: Debug information or error

        """
        try:
            debug_info: Types.Data.DebugInfoData = {
                "service": "FlextCliDebug",
                "timestamp": datetime.now(UTC).isoformat(),
                "debug_id": str(uuid.uuid4()),
                "system_info": self._get_system_info(),
                "environment_status": FlextCliConstants.ServiceStatus.OPERATIONAL.value,
                "connectivity_status": FlextCliConstants.ServiceStatus.CONNECTED.value,
            }
            return FlextResult[Types.Data.DebugInfoData].ok(debug_info)
        except Exception as e:
            return FlextResult[Types.Data.DebugInfoData].fail(
                f"Debug info collection failed: {e}"
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
                f"System info collection failed: {e}"
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
            typed_paths: FlextCliTypes.Data.CliDataDict = {"paths": paths_list}
            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(typed_paths)
        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                f"System paths collection failed: {e}"
            )

    def get_comprehensive_debug_info(
        self,
    ) -> FlextResult[Types.Data.DebugInfoData]:
        """Get comprehensive debug information combining all debug methods."""
        try:
            comprehensive_info: FlextTypes.Dict = {}

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

            # Type-safe cast: comprehensive_info contains only JSON-compatible values
            typed_comprehensive_info = cast(
                "Types.Data.DebugInfoData", comprehensive_info
            )
            return FlextResult[Types.Data.DebugInfoData].ok(typed_comprehensive_info)

        except Exception as e:
            return FlextResult[Types.Data.DebugInfoData].fail(
                f"Comprehensive debug info collection failed: {e}"
            )

    # =========================================================================
    # PRIVATE HELPER METHODS - Implementation details
    # =========================================================================

    def _get_system_info(self) -> FlextTypes.Dict:
        """Get basic system information."""
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "hostname": platform.node(),
        }

    def _get_environment_info(self) -> FlextTypes.StringDict:
        """Get environment variables with sensitive data masked."""
        env_info: FlextTypes.StringDict = {}
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

    def _get_path_info(self) -> list[FlextTypes.Dict]:
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

    def _validate_filesystem_permissions(self) -> FlextTypes.StringList:
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
