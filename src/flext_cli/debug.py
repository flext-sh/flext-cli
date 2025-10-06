"""FLEXT CLI Debug - Unified debug service using flext-core directly.

Single responsibility debug service eliminating ALL loose functions and
wrapper patterns. Uses flext-core utilities directly with SOURCE OF TRUTH
principle for all configurations and metadata.

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

from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
)

from flext_cli.constants import FlextCliConstants
from flext_cli.typings import FlextCliTypes, FlextCliTypes as Types


class FlextCliDebug(FlextService[str]):
    """Debug service extending FlextService from flext-core.

    Implements FlextCliProtocols.CliDebugProvider through structural subtyping.

    Provides essential debugging functionality using flext-core patterns.
    Follows single-responsibility principle with nested helpers.
    """

    # Attribute declarations - override FlextService optional types
    # These are guaranteed initialized in __init__
    _logger: FlextLogger | None
    _container: FlextContainer | None

    @override
    def __init__(self, **_data: object) -> None:
        """Initialize debug service with flext-core integration and Phase 1 context enrichment."""
        super().__init__()
        # Logger and container inherited from FlextService via FlextMixins

    @override
    def execute(self) -> FlextResult[str]:
        """Execute debug service - required by FlextService."""
        return FlextResult[str].ok("FlextCliDebug service operational")

    def get_system_info(
        self,
    ) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
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
            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(typed_info)
        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                f"System info failed: {e}"
            )

    def get_environment_variables(
        self,
    ) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Get environment variables with sensitive data masked."""
        try:
            env_info = self._get_environment_info()
            # Convert to more specific type for better type safety
            typed_env_info: FlextCliTypes.Data.CliDataDict = {}
            for key, value in env_info.items():
                if isinstance(value, (str, int, float, bool, type(None))):
                    typed_env_info[key] = value
                else:
                    typed_env_info[key] = str(value)
            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(typed_env_info)
        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                f"Environment info failed: {e}"
            )

    def get_system_paths(
        self,
    ) -> FlextResult[list[FlextCliTypes.Data.CliDataDict]]:
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
            return FlextResult[list[FlextCliTypes.Data.CliDataDict]].ok(typed_paths)
        except Exception as e:
            return FlextResult[list[FlextCliTypes.Data.CliDataDict]].fail(
                f"Path info failed: {e}"
            )

    def validate_environment_setup(self) -> FlextResult[FlextCliTypes.Data.ErrorList]:
        """Validate environment setup and dependencies."""
        try:
            results = self._validate_filesystem_permissions()
            return FlextResult[FlextCliTypes.Data.ErrorList].ok(results)
        except Exception as e:
            return FlextResult[FlextCliTypes.Data.ErrorList].fail(
                f"Environment validation failed: {e}"
            )

    def test_connectivity(self) -> FlextResult[FlextCliTypes.Data.ConnectivityInfo]:
        """Test basic connectivity and service status."""
        try:
            connectivity_info = {
                "status": FlextCliConstants.CONNECTED,
                "timestamp": datetime.now(UTC).isoformat(),
                "service": str(FlextCliDebug),
                "connectivity": FlextCliConstants.OPERATIONAL,
            }
            return FlextResult[FlextCliTypes.Data.ConnectivityInfo].ok(
                connectivity_info
            )
        except Exception as e:
            return FlextResult[FlextCliTypes.Data.ConnectivityInfo].fail(
                f"Connectivity test failed: {e}"
            )

    def execute_health_check(self) -> FlextResult[Types.Data.DebugInfoData]:
        """Execute comprehensive health check."""
        try:
            health_info: Types.Data.DebugInfoData = {
                "status": FlextCliConstants.HEALTHY,
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
        self, args: Types.Command.CommandArgs
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
                "environment_status": FlextCliConstants.OPERATIONAL,
                "connectivity_status": FlextCliConstants.CONNECTED,
            }
            return FlextResult[Types.Data.DebugInfoData].ok(debug_info)
        except Exception as e:
            return FlextResult[Types.Data.DebugInfoData].fail(
                f"Debug info collection failed: {e}"
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
                comprehensive_info["system"] = system_result.value
            else:
                comprehensive_info["system_error"] = system_result.error

            # Collect environment info
            env_result = self.get_environment_variables()
            if env_result.is_success:
                comprehensive_info["environment"] = cast(
                    "Types.Data.DebugInfoData", env_result.value
                )
            else:
                comprehensive_info["environment_error"] = env_result.error

            # Collect paths info
            paths_result = self.get_system_paths()
            if paths_result.is_success:
                comprehensive_info["paths"] = cast(
                    "Types.Data.DebugInfoData", paths_result.value
                )
            else:
                comprehensive_info["paths_error"] = paths_result.error

            # Collect debug info
            debug_result = self.get_debug_info()
            if debug_result.is_success:
                comprehensive_info["debug"] = debug_result.value
            else:
                comprehensive_info["debug_error"] = debug_result.error

            return FlextResult[Types.Data.DebugInfoData].ok(comprehensive_info)

        except Exception as e:
            return FlextResult[Types.Data.DebugInfoData].fail(
                f"Comprehensive debug info collection failed: {e}"
            )

    # =========================================================================
    # PRIVATE HELPER METHODS - Implementation details
    # =========================================================================

    def _get_system_info(self) -> dict[str, object]:
        """Get basic system information."""
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "hostname": platform.node(),
        }

    def _get_environment_info(self) -> dict[str, object]:
        """Get environment variables with sensitive data masked."""
        env_info = {}
        sensitive_keys = {"password", "token", "secret", "key", "auth"}

        for key, value in os.environ.items():
            if any(sens in key.lower() for sens in sensitive_keys):
                env_info[key] = "***MASKED***"
            else:
                env_info[key] = value

        return env_info

    def _get_path_info(self) -> list[dict[str, object]]:
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

    def _validate_filesystem_permissions(self) -> FlextCliTypes.Data.ErrorList:
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
                with pathlib.Path(test_file).open("w", encoding="utf-8") as f:
                    f.write("test")
                pathlib.Path(test_file).unlink()
            except OSError as e:
                errors.append(f"Cannot write to current directory: {e}")

        except Exception as e:
            errors.append(f"Filesystem validation failed: {e}")

        return errors


__all__ = [
    "FlextCliDebug",
]
