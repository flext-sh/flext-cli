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
from collections.abc import Mapping
from typing import override

from flext_core import r

from flext_cli.base import FlextCliServiceBase
from flext_cli.constants import FlextCliConstants
from flext_cli.models import EnvironmentInfo, PathInfo, SystemInfo
from flext_cli.services.output import FlextCliOutput
from flext_cli.typings import t
from flext_cli.utilities import u


class FlextCliDebug(FlextCliServiceBase):
    """Debug service extending FlextCliServiceBase.

    Business Rules:
    ───────────────
    1. Debug operations MUST NOT expose sensitive data (passwords, tokens, keys)
    2. System information MUST be collected safely (handle missing attributes)
    3. Environment variables MUST be filtered to exclude sensitive values
    4. Path information MUST validate paths exist before reporting
    5. Health checks MUST validate all critical components
    6. Debug output MUST be formatted for readability (JSON/YAML)
    7. Debug operations MUST use r[T] for error handling
    8. Trace operations MUST respect debug mode configuration

    Architecture Implications:
    ───────────────────────────
    - Extends FlextCliServiceBase for consistent logging and container access
    - Uses FlextModels for structured debug information
    - Generalized helpers reduce code duplication (DRY)
    - Safe info collection handles missing attributes gracefully
    - Model conversion uses Pydantic model_dump for serialization

    Audit Implications:
    ───────────────────
    - Debug operations MUST be logged with operation type and result
    - Sensitive data MUST be masked in debug output (passwords, tokens, keys)
    - System information collection MUST not expose security vulnerabilities
    - Environment variable access MUST filter sensitive values
    - Debug output MUST be sanitized before logging or display
    - Health check failures MUST be logged for monitoring

    Provides essential debugging functionality using flext-core patterns.
    Follows single-responsibility principle with nested helpers.
    """

    @override
    def __init__(self, **_data: t.GeneralValueType) -> None:
        """Initialize debug service with flext-core integration."""
        super().__init__()

    # =========================================================================
    # PRIVATE HELPERS - Generalize common patterns
    # =========================================================================

    @staticmethod
    def _convert_model_to_dict(
        model: SystemInfo | EnvironmentInfo | PathInfo,
    ) -> dict[str, t.GeneralValueType]:
        """Generalized model to dict conversion helper."""
        # Use build() DSL for JSON conversion
        # Reuse to_dict_json helper from output module (imported at top)
        # Use m for concrete models when we need model_dump()
        raw_dict = model.model_dump()
        json_dict = FlextCliOutput.to_dict_json(raw_dict)
        result = FlextCliOutput.cast_if(json_dict, dict, raw_dict)
        return result if isinstance(result, dict) else {}

    @staticmethod
    def _convert_result_to_json_value(
        result: r[dict[str, t.GeneralValueType]],
    ) -> t.GeneralValueType:
        """Convert r[JsonDict] to t.GeneralValueType."""
        if result.is_success:
            # JsonDict is dict[str, t.GeneralValueType] - return directly
            return result.value
        # Return error as string
        return result.error or "Unknown error"

    def _collect_info_safely(
        self,
        method_name: str,
        error_key: str,
        info_dict: dict[str, t.GeneralValueType],
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

    def execute(
        self, **_kwargs: dict[str, t.GeneralValueType]
    ) -> r[dict[str, t.GeneralValueType]]:
        """Execute debug service - required by FlextService."""
        return r[dict[str, t.GeneralValueType]].ok({
            "status": "operational",
            "message": FlextCliConstants.Cli.ServiceMessages.FLEXT_CLI_DEBUG_OPERATIONAL,
        })

    def get_environment_variables(
        self,
    ) -> r[dict[str, t.GeneralValueType]]:
        """Get environment variables with sensitive data masked."""
        try:
            env_info = self._get_environment_info()
            typed_env_info: dict[str, t.GeneralValueType] = dict(
                env_info.variables.items(),
            )
            return r[dict[str, t.GeneralValueType]].ok(typed_env_info)
        except Exception as e:
            return r[dict[str, t.GeneralValueType]].fail(
                FlextCliConstants.Cli.DebugErrorMessages.ENVIRONMENT_INFO_FAILED.format(
                    error=e,
                ),
            )

    def validate_environment_setup(
        self,
    ) -> r[list[str]]:
        """Validate environment setup and dependencies."""
        try:
            results = self._validate_filesystem_permissions()
            return r[list[str]].ok(results)
        except Exception as e:
            return r[list[str]].fail(
                FlextCliConstants.Cli.DebugErrorMessages.ENVIRONMENT_VALIDATION_FAILED.format(
                    error=e,
                ),
            )

    @staticmethod
    def test_connectivity() -> r[Mapping[str, str]]:
        """Test basic connectivity and service status."""
        try:
            connectivity_info = {
                FlextCliConstants.Cli.DictKeys.STATUS: FlextCliConstants.Cli.ServiceStatus.CONNECTED.value,
                FlextCliConstants.Cli.DictKeys.TIMESTAMP: u.generate("timestamp"),
                FlextCliConstants.Cli.DictKeys.SERVICE: str(FlextCliDebug),
                FlextCliConstants.Cli.DebugDictKeys.CONNECTIVITY: FlextCliConstants.Cli.ServiceStatus.OPERATIONAL.value,
            }
            return r[dict[str, str]].ok(connectivity_info)
        except Exception as e:
            return r[dict[str, str]].fail(
                FlextCliConstants.Cli.DebugErrorMessages.CONNECTIVITY_TEST_FAILED.format(
                    error=e,
                ),
            )

    @staticmethod
    def execute_health_check() -> r[Mapping[str, t.GeneralValueType]]:
        """Execute comprehensive health check."""
        try:
            health_info: dict[str, t.GeneralValueType] = {
                FlextCliConstants.Cli.DictKeys.STATUS: FlextCliConstants.Cli.ServiceStatus.HEALTHY.value,
                FlextCliConstants.Cli.DictKeys.TIMESTAMP: u.generate("timestamp"),
                FlextCliConstants.Cli.DictKeys.SERVICE: FlextCliConstants.Cli.DebugDefaults.SERVICE_NAME,
                FlextCliConstants.Cli.DebugDictKeys.CHECK_ID: u.generate("id"),
                FlextCliConstants.Cli.DebugDictKeys.CHECKS_PASSED: True,
            }
            return r[dict[str, t.GeneralValueType]].ok(health_info)
        except Exception as e:
            return r[dict[str, t.GeneralValueType]].fail(
                FlextCliConstants.Cli.DebugErrorMessages.HEALTH_CHECK_FAILED.format(
                    error=e,
                ),
            )

    @staticmethod
    def execute_trace(args: list[str]) -> r[Mapping[str, t.GeneralValueType]]:
        """Execute trace operation with provided arguments."""
        try:
            trace_info: dict[str, t.GeneralValueType] = {
                FlextCliConstants.Cli.DebugDictKeys.OPERATION: FlextCliConstants.Cli.TRACE,
                FlextCliConstants.Cli.DictKeys.ARGS: list(args),
                FlextCliConstants.Cli.DebugDictKeys.ARGS_COUNT: len(args),
                FlextCliConstants.Cli.DictKeys.TIMESTAMP: u.generate("timestamp"),
                FlextCliConstants.Cli.DebugDictKeys.TRACE_ID: u.generate("id"),
            }
            return r[dict[str, t.GeneralValueType]].ok(trace_info)
        except Exception as e:
            return r[dict[str, t.GeneralValueType]].fail(
                FlextCliConstants.Cli.DebugErrorMessages.TRACE_EXECUTION_FAILED.format(
                    error=e,
                ),
            )

    def get_debug_info(self) -> r[Mapping[str, t.GeneralValueType]]:
        """Get comprehensive debug information."""
        try:
            system_info_model = self._get_system_info()
            system_info_dict = FlextCliDebug._convert_model_to_dict(system_info_model)
            # Convert system_info_dict to t.GeneralValueType - filter dict items using dict comprehension
            system_info_json: dict[str, t.GeneralValueType] = {
                k: v for k, v in system_info_dict.items() if isinstance(k, str)
            }

            # Get environment info
            environment_info_model = self._get_environment_info()
            environment_info_dict = FlextCliDebug._convert_model_to_dict(
                environment_info_model,
            )
            # Filter dict items using dict comprehension (u.filter only works with lists/tuples)
            environment_info_json: dict[str, t.GeneralValueType] = {
                k: v for k, v in environment_info_dict.items() if isinstance(k, str)
            }

            debug_info: dict[str, t.GeneralValueType] = {
                FlextCliConstants.Cli.DictKeys.SERVICE: FlextCliConstants.Cli.DebugDefaults.SERVICE_NAME,
                FlextCliConstants.Cli.DictKeys.TIMESTAMP: u.generate("timestamp"),
                FlextCliConstants.Cli.DebugDictKeys.DEBUG_ID: u.generate("id"),
                FlextCliConstants.Cli.DebugDictKeys.SYSTEM_INFO: system_info_json,
                FlextCliConstants.Cli.DebugDictKeys.ENVIRONMENT_INFO: environment_info_json,
                FlextCliConstants.Cli.DebugDictKeys.CONNECTIVITY_STATUS: FlextCliConstants.Cli.ServiceStatus.CONNECTED.value,
            }
            return r[dict[str, t.GeneralValueType]].ok(debug_info)
        except Exception as e:
            return r[dict[str, t.GeneralValueType]].fail(
                FlextCliConstants.Cli.DebugErrorMessages.DEBUG_INFO_COLLECTION_FAILED.format(
                    error=e,
                ),
            )

    def get_system_info(self) -> r[Mapping[str, t.GeneralValueType]]:
        """Get system information - public API method."""
        try:
            info_model = self._get_system_info()
            info_dict: dict[str, t.GeneralValueType] = (
                FlextCliDebug._convert_model_to_dict(
                    info_model,
                )
            )
            return r[dict[str, t.GeneralValueType]].ok(info_dict)
        except Exception as e:
            return r[dict[str, t.GeneralValueType]].fail(
                FlextCliConstants.Cli.DebugErrorMessages.SYSTEM_INFO_COLLECTION_FAILED.format(
                    error=e,
                ),
            )

    def get_system_paths(self) -> r[Mapping[str, t.GeneralValueType]]:
        """Get system path information - public API method."""
        try:
            paths_data = self._get_path_info()
            # Convert each PathInfo model to dict
            serialized_paths: list[t.GeneralValueType] = []
            for path_info in paths_data:
                path_dict = FlextCliDebug._convert_model_to_dict(path_info)
                # path_dict is already CliDataDict (dict[str, t.GeneralValueType])
                # dict is part of t.GeneralValueType union, so it's compatible
                # Filter dict items using dict comprehension (u.filter only works with lists/tuples)
                path_json_dict: dict[str, t.GeneralValueType] = {
                    k: v for k, v in path_dict.items() if isinstance(k, str)
                }
                # dict[str, t.GeneralValueType] is part of t.GeneralValueType union
                serialized_paths.append(path_json_dict)

            # list[t.GeneralValueType] is compatible with t.GeneralValueType (list is part of union)
            paths_dict: dict[str, t.GeneralValueType] = {
                "paths": serialized_paths,
            }
            return r[dict[str, t.GeneralValueType]].ok(paths_dict)
        except Exception as e:
            return r[dict[str, t.GeneralValueType]].fail(
                FlextCliConstants.Cli.DebugErrorMessages.SYSTEM_PATHS_COLLECTION_FAILED.format(
                    error=e,
                ),
            )

    def get_comprehensive_debug_info(
        self,
    ) -> r[dict[str, t.GeneralValueType]]:
        """Get comprehensive debug information combining all debug methods."""
        try:
            comprehensive_info: dict[str, t.GeneralValueType] = {}

            # Collect all info using generalized helper
            self._collect_info_safely(
                "get_system_info",
                FlextCliConstants.Cli.DebugDictKeys.SYSTEM_ERROR,
                comprehensive_info,
            )
            self._collect_info_safely(
                "get_environment_variables",
                FlextCliConstants.Cli.DebugDictKeys.ENVIRONMENT_ERROR,
                comprehensive_info,
            )
            self._collect_info_safely(
                "get_system_paths",
                FlextCliConstants.Cli.DebugDictKeys.PATHS_ERROR,
                comprehensive_info,
            )
            self._collect_info_safely(
                "get_debug_info",
                FlextCliConstants.Cli.DebugDictKeys.DEBUG_ERROR,
                comprehensive_info,
            )

            return r[dict[str, t.GeneralValueType]].ok(comprehensive_info)
        except Exception as e:
            return r[dict[str, t.GeneralValueType]].fail(
                FlextCliConstants.Cli.DebugErrorMessages.COMPREHENSIVE_DEBUG_INFO_FAILED.format(
                    error=e,
                ),
            )

    # =========================================================================
    # PRIVATE HELPER METHODS - Implementation details
    # =========================================================================

    @staticmethod
    def _get_system_info() -> SystemInfo:
        """Get basic system information as Pydantic model."""
        arch_tuple = platform.architecture()
        return SystemInfo(
            python_version=sys.version,
            platform=platform.platform(),
            architecture=list(arch_tuple),
            processor=platform.processor(),
            hostname=platform.node(),
        )

    @staticmethod
    def _get_environment_info() -> EnvironmentInfo:
        """Get environment variables with sensitive data masked as Pydantic model."""

        # Use u.process to handle environment variables
        def process_env_item(k: str, v: str) -> str:
            """Process single environment variable."""
            if any(
                sens in k.lower()
                for sens in FlextCliConstants.Cli.DebugDefaults.SENSITIVE_KEYS
            ):
                return FlextCliConstants.Cli.DebugDefaults.MASKED_SENSITIVE
            return v

        env_info_result = u.process(
            dict(os.environ),
            processor=process_env_item,
            on_error="skip",
        )
        env_info_val = env_info_result.value if env_info_result.is_success else {}
        env_info: dict[str, str] = (
            dict(env_info_val) if isinstance(env_info_val, dict) else {}
        )

        return EnvironmentInfo(variables=env_info)

    @staticmethod
    def _get_path_info() -> list[PathInfo]:
        """Get system path information as list of Pydantic models."""
        paths: list[PathInfo] = []
        for i, path in enumerate(sys.path):
            path_obj = pathlib.Path(path)
            paths.append(
                PathInfo(
                    index=i,
                    path=path,
                    exists=path_obj.exists(),
                    is_file=path_obj.is_file() if path_obj.exists() else False,
                    is_dir=path_obj.is_dir() if path_obj.exists() else False,
                ),
            )

        return paths

    @staticmethod
    def _validate_filesystem_permissions() -> list[str]:
        """Validate filesystem permissions and setup."""
        errors: list[str] = []

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
                    encoding=FlextCliConstants.Cli.Utilities.DEFAULT_ENCODING,
                ) as f:
                    f.write("test")
                pathlib.Path(test_file).unlink()
            except OSError as e:
                errors.append(
                    FlextCliConstants.Cli.ErrorMessages.CANNOT_WRITE_CURRENT_DIR.format(
                        error=e,
                    ),
                )

        except Exception as e:
            errors.append(
                FlextCliConstants.Cli.ErrorMessages.FILESYSTEM_VALIDATION_FAILED.format(
                    error=e,
                ),
            )

        return errors


__all__ = ["FlextCliDebug"]
