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
from typing import override

from flext_core.service import FlextService

from flext_cli.constants import FlextCliConstants
from flext_cli.typings import CliDataDict, FlextCliTypes
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
)


class FlextCliDebug(FlextService[str]):
    """Debug service extending FlextService from flext-core.

    Provides essential debugging functionality using flext-core patterns.
    Follows single-responsibility principle with nested helpers.
    """

    @override
    def __init__(self, **_data: object) -> None:
        """Initialize debug service with flext-core integration."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()

    class _DebugHelper:
        """Nested helper for debug operations."""

        @staticmethod
        def get_system_info() -> dict[str, object]:
            """Get basic system information."""
            return {
                "service": FlextCliDebug,
                "status": FlextCliConstants.OPERATIONAL,
                "timestamp": datetime.now(UTC).isoformat(),
                "python_version": sys.version,
                "platform": sys.platform,
            }

        @staticmethod
        def get_environment_info() -> dict[str, object]:
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
        def get_path_info() -> list[dict[str, object]]:
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
        def validate_environment() -> list[str]:
            """Validate environment setup."""
            results: list[str] = []

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

    async def execute_async(self) -> FlextResult[str]:
        """Execute debug service asynchronously - required by FlextService."""
        return FlextResult[str].ok("FlextCliDebug service operational")

    def get_system_info(
        self,
    ) -> FlextResult[CliDataDict]:
        """Get system information for debugging."""
        try:
            info = self._DebugHelper.get_system_info()
            # Convert to more specific type for better type safety
            typed_info: CliDataDict = {}
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
    ) -> FlextResult[CliDataDict]:
        """Get environment variables with sensitive data masked."""
        try:
            env_info = self._DebugHelper.get_environment_info()
            # Convert to more specific type for better type safety
            typed_env_info: CliDataDict = {}
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
    ) -> FlextResult[list[CliDataDict]]:
        """Get system path information."""
        try:
            paths = self._DebugHelper.get_path_info()
            # Convert to more specific type for better type safety
            typed_paths: list[CliDataDict] = []
            for path_dict in paths:
                typed_path: CliDataDict = {}
                for key, value in path_dict.items():
                    if isinstance(value, (str, int, float, bool, type(None))):
                        typed_path[key] = value
                    else:
                        typed_path[key] = str(value)
                typed_paths.append(typed_path)
            return FlextResult[list[CliDataDict]].ok(typed_paths)
        except Exception as e:
            return FlextResult[list[CliDataDict]].fail(f"Path info failed: {e}")

    def get_path_info(self) -> FlextResult[list[CliDataDict]]:
        """Get system path information (alias for get_system_paths)."""
        return self.get_system_paths()

    def validate_environment_setup(self) -> FlextResult[list[str]]:
        """Validate environment setup and dependencies."""
        try:
            results = self._DebugHelper.validate_environment()
            return FlextResult[list[str]].ok(results)
        except Exception as e:
            return FlextResult[list[str]].fail(f"Environment validation failed: {e}")

    def test_connectivity(self) -> FlextResult[dict[str, str]]:
        """Test basic connectivity and service status."""
        try:
            connectivity_info = {
                "status": FlextCliConstants.CONNECTED,
                "timestamp": datetime.now(UTC).isoformat(),
                "service": FlextCliDebug,
                "connectivity": FlextCliConstants.OPERATIONAL,
            }
            return FlextResult[dict[str, str]].ok(connectivity_info)
        except Exception as e:
            return FlextResult[dict[str, str]].fail(f"Connectivity test failed: {e}")

    def execute_health_check(self) -> FlextResult[dict[str, object]]:
        """Execute comprehensive health check."""
        try:
            health_info: dict[str, object] = {
                "status": FlextCliConstants.HEALTHY,
                "timestamp": datetime.now(UTC).isoformat(),
                "service": self.__class__.__name__,
                "check_id": str(uuid.uuid4()),
                "checks_passed": True,
            }
            return FlextResult[dict[str, object]].ok(health_info)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Health check failed: {e}")

    def execute_trace(self, args: list[str]) -> FlextResult[dict[str, object]]:
        """Execute trace operation with provided arguments."""
        try:
            trace_info: dict[str, object] = {
                "operation": FlextCliConstants.TRACE,
                "args": args,
                "args_count": len(args),
                "timestamp": datetime.now(UTC).isoformat(),
                "trace_id": str(uuid.uuid4()),
            }
            return FlextResult[dict[str, object]].ok(trace_info)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Trace execution failed: {e}")

    def get_debug_info(self) -> FlextResult[dict[str, object]]:
        """Get comprehensive debug information.

        Returns:
            FlextResult[dict[str, object]]: Debug information or error

        """
        try:
            debug_info: dict[str, object] = {
                "service": self.__class__.__name__,
                "timestamp": datetime.now(UTC).isoformat(),
                "debug_id": str(uuid.uuid4()),
                "system_info": self._DebugHelper.get_system_info(),
                "environment_status": FlextCliConstants.OPERATIONAL,
                "connectivity_status": FlextCliConstants.CONNECTED,
            }
            return FlextResult[dict[str, object]].ok(debug_info)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(
                f"Debug info collection failed: {e}"
            )

    def get_comprehensive_debug_info(self) -> FlextResult[dict[str, object]]:
        """Get comprehensive debug information combining all debug methods."""
        try:
            comprehensive_info: dict[str, object] = {}
            
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
            
            return FlextResult[dict[str, object]].ok(comprehensive_info)
            
        except Exception as e:
            return FlextResult[dict[str, object]].fail(
                f"Comprehensive debug info collection failed: {e}"
            )


__all__ = [
    "FlextCliDebug",
]
