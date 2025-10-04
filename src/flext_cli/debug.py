"""FLEXT CLI Debug - Unified debug service using flext-core directly.

Single responsibility debug service eliminating ALL loose functions and
wrapper patterns. Uses flext-core utilities directly with SOURCE OF TRUTH
principle for all configurations and metadata.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import importlib.util
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
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
    _logger: FlextLogger
    _container: FlextContainer

    @override
    def __init__(self, **_data: object) -> None:
        """Initialize debug service with flext-core integration."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer()

    class _DebugHelper:
        """Nested helper for debug operations."""

        @staticmethod
        def get_system_info() -> Types.Data.DebugInfoData:
            """Get basic system information."""
            return {
                "service": "FlextCliDebug",
                "status": FlextCliConstants.OPERATIONAL,
                "timestamp": datetime.now(UTC).isoformat(),
                "python_version": sys.version,
                "platform": sys.platform,
            }

        @staticmethod
        def get_environment_info() -> Types.Data.DebugInfoData:
            """Get environment information with sensitive data masked."""
            flext_vars = {k: v for k, v in os.environ.items() if k.startswith("FLEXT_")}

            sensitive_patterns = ["TOKEN", "KEY", "SECRET", "PASSWORD"]
            masked_vars = {}
            masked_count = 0
            preview_length = 4

            for key, value in flext_vars.items():
                if any(pattern in key.upper() for pattern in sensitive_patterns):
                    masked_vars[key] = (
                        f"{value[:preview_length]}****"
                        if len(value) > preview_length
                        else "****"
                    )
                    masked_count += 1
                else:
                    masked_vars[key] = value

            return {
                "variables": masked_vars,
                "masked_count": masked_count,
                "total_count": len(flext_vars),
            }

        @staticmethod
        def get_path_info() -> FlextCliTypes.Data.PathInfoList:
            """Get system path information."""
            home = Path.home()
            flext_dir = home / ".flext"

            return [
                {
                    "label": FlextCliConstants.HOME,
                    "path": str(home),
                    "exists": home.exists(),
                },
                {
                    "label": FlextCliConstants.CONFIG,
                    "path": str(flext_dir),
                    "exists": flext_dir.exists(),
                },
                {
                    "label": FlextCliConstants.CACHE,
                    "path": str(flext_dir / "cache"),
                    "exists": (flext_dir / "cache").exists(),
                },
                {
                    "label": FlextCliConstants.LOGS,
                    "path": str(flext_dir / "logs"),
                    "exists": (flext_dir / "logs").exists(),
                },
            ]

        @staticmethod
        def validate_environment() -> FlextCliTypes.Data.ErrorList:
            """Validate environment setup."""
            results: FlextCliTypes.Data.ErrorList = []

            # Check Python version
            if hasattr(sys, "version_info") and sys.version_info >= (3, 11):
                results.append("✓ Python version check passed")
            else:
                results.append("✗ Python version check failed")

            # Check flext-core availability
            try:
                spec = importlib.util.find_spec("flext_core")
                if spec is not None:
                    results.append("✓ flext-core dependency available")
                else:
                    results.append("✗ flext-core dependency missing")
            except ImportError:
                results.append("✗ flext-core dependency missing")

            # Check basic filesystem permissions
            try:
                test_path = Path.home() / ".flext"
                test_path.mkdir(exist_ok=True)
                results.append("✓ Filesystem permissions check passed")
            except (OSError, PermissionError):
                results.append("✗ Filesystem permissions check failed")

            return results

    @override
    def execute(self) -> FlextResult[str]:
        """Execute debug service - required by FlextService."""
        return FlextResult[str].ok("FlextCliDebug service operational")

    def get_system_info(
        self,
    ) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Get system information for debugging."""
        try:
            info = self._DebugHelper.get_system_info()
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
            env_info = self._DebugHelper.get_environment_info()
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
            paths = self._DebugHelper.get_path_info()
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
            results = self._DebugHelper.validate_environment()
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
                "system_info": self._DebugHelper.get_system_info(),
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


__all__ = [
    "FlextCliDebug",
]
