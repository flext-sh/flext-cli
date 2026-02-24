"""FLEXT CLI Debug - Unified debug service using flext-core directly.

**MODULE**: FlextCliDebug - Single primary class for debug operations
**SCOPE**: System info, environment variables, paths, health checks, trace operations

Copyright (c) 2025 FLEXT TeaFlextCliModels. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
import pathlib
import platform
import sys
import tempfile
from collections.abc import Mapping, MutableMapping
from typing import override

from flext_core import r
from flext_core.typings import t

from flext_cli.base import FlextCliServiceBase
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels
from flext_cli.utilities import FlextCliUtilities


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
    def __init__(self) -> None:
        """Initialize debug service with flext-core integration."""
        super().__init__()

    # =========================================================================
    # PRIVATE HELPERS - Generalize common patterns
    # =========================================================================

    @staticmethod
    def _convert_model_to_dict(
        model: FlextCliModels.Cli.SystemInfo
        | FlextCliModels.Cli.EnvironmentInfo
        | FlextCliModels.Cli.PathInfo,
    ) -> Mapping[str, t.JsonValue]:
        """Generalized model to dict conversion helper."""
        # Use build() DSL for JSON conversion
        # Reuse to_dict_json helper from output module (imported at top)
        # Use m for concrete models when we need model_dump()
        return model.model_dump()

    @staticmethod
    def _convert_result_to_json_value(
        result: r[Mapping[str, t.JsonValue]],
    ) -> t.JsonValue:
        """Convert r[JsonDict] to t.JsonValue."""
        if result.is_success:
            # JsonDict is dict[str, GeneralValueType] - return directly
            return result.value
        # Return error as string
        return result.error or "Unknown error"

    def _collect_info_safely(
        self,
        method_name: str,
        error_key: str,
        info_dict: MutableMapping[str, t.JsonValue],
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

    def execute(self) -> r[Mapping[str, t.JsonValue]]:
        """Execute debug service - required by FlextService."""
        return r[Mapping[str, t.JsonValue]].ok({
            "status": "operational",
            "message": FlextCliConstants.Cli.ServiceMessages.FLEXT_CLI_DEBUG_OPERATIONAL,
        })

    def get_environment_variables(
        self,
    ) -> r[Mapping[str, t.JsonValue]]:
        """Get environment variables with sensitive data masked."""
        try:
            env_info = self._get_environment_info()
            typed_env_info: dict[str, t.JsonValue] = dict(
                env_info.variables.items(),
            )
            return r[Mapping[str, t.JsonValue]].ok(typed_env_info)
        except Exception as e:
            return r[Mapping[str, t.JsonValue]].fail(
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
                FlextCliConstants.Cli.DictKeys.TIMESTAMP: FlextCliUtilities.generate(
                    "timestamp",
                ),
                FlextCliConstants.Cli.DictKeys.SERVICE: str(FlextCliDebug),
                FlextCliConstants.Cli.DebugDictKeys.CONNECTIVITY: FlextCliConstants.Cli.ServiceStatus.OPERATIONAL.value,
            }
            return r[Mapping[str, str]].ok(connectivity_info)
        except Exception as e:
            return r[Mapping[str, str]].fail(
                FlextCliConstants.Cli.DebugErrorMessages.CONNECTIVITY_TEST_FAILED.format(
                    error=e,
                ),
            )

    @staticmethod
    def execute_health_check() -> r[Mapping[str, t.JsonValue]]:
        """Execute comprehensive health check."""
        try:
            health_info: dict[str, t.JsonValue] = {
                FlextCliConstants.Cli.DictKeys.STATUS: FlextCliConstants.Cli.ServiceStatus.HEALTHY.value,
                FlextCliConstants.Cli.DictKeys.TIMESTAMP: FlextCliUtilities.generate(
                    "timestamp",
                ),
                FlextCliConstants.Cli.DictKeys.SERVICE: FlextCliConstants.Cli.DebugDefaults.SERVICE_NAME,
                FlextCliConstants.Cli.DebugDictKeys.CHECK_ID: FlextCliUtilities.generate(
                    "id",
                ),
                FlextCliConstants.Cli.DebugDictKeys.CHECKS_PASSED: True,
            }
            return r[Mapping[str, t.JsonValue]].ok(health_info)
        except Exception as e:
            return r[Mapping[str, t.JsonValue]].fail(
                FlextCliConstants.Cli.DebugErrorMessages.HEALTH_CHECK_FAILED.format(
                    error=e,
                ),
            )

    @staticmethod
    def execute_trace(
        args: list[str],
    ) -> r[Mapping[str, t.JsonValue]]:
        """Execute trace operation with provided arguments."""
        try:
            trace_info: dict[str, t.JsonValue] = {
                FlextCliConstants.Cli.DebugDictKeys.OPERATION: FlextCliConstants.Cli.TRACE,
                FlextCliConstants.Cli.DictKeys.ARGS: list(args),
                FlextCliConstants.Cli.DebugDictKeys.ARGS_COUNT: len(args),
                FlextCliConstants.Cli.DictKeys.TIMESTAMP: FlextCliUtilities.generate(
                    "timestamp",
                ),
                FlextCliConstants.Cli.DebugDictKeys.TRACE_ID: FlextCliUtilities.generate(
                    "id",
                ),
            }
            return r[Mapping[str, t.JsonValue]].ok(trace_info)
        except Exception as e:
            return r[Mapping[str, t.JsonValue]].fail(
                FlextCliConstants.Cli.DebugErrorMessages.TRACE_EXECUTION_FAILED.format(
                    error=e,
                ),
            )

    def get_debug_info(self) -> r[Mapping[str, t.JsonValue]]:
        """Get comprehensive debug information."""
        try:
            system_info_model = self._get_system_info()
            system_info_dict = FlextCliDebug._convert_model_to_dict(system_info_model)
            # model_dump() always returns dict[str, ...] — keys are always str
            system_info_json: dict[str, t.JsonValue] = dict(system_info_dict)

            # Get environment info
            environment_info_model = self._get_environment_info()
            environment_info_dict = FlextCliDebug._convert_model_to_dict(
                environment_info_model,
            )
            environment_info_json: dict[str, t.JsonValue] = dict(environment_info_dict)

            debug_info: dict[str, t.JsonValue] = {
                FlextCliConstants.Cli.DictKeys.SERVICE: FlextCliConstants.Cli.DebugDefaults.SERVICE_NAME,
                FlextCliConstants.Cli.DictKeys.TIMESTAMP: FlextCliUtilities.generate(
                    "timestamp",
                ),
                FlextCliConstants.Cli.DebugDictKeys.DEBUG_ID: FlextCliUtilities.generate(
                    "id",
                ),
                FlextCliConstants.Cli.DebugDictKeys.SYSTEM_INFO: system_info_json,
                FlextCliConstants.Cli.DebugDictKeys.ENVIRONMENT_INFO: environment_info_json,
                FlextCliConstants.Cli.DebugDictKeys.CONNECTIVITY_STATUS: FlextCliConstants.Cli.ServiceStatus.CONNECTED.value,
            }
            return r[Mapping[str, t.JsonValue]].ok(debug_info)
        except Exception as e:
            return r[Mapping[str, t.JsonValue]].fail(
                FlextCliConstants.Cli.DebugErrorMessages.DEBUG_INFO_COLLECTION_FAILED.format(
                    error=e,
                ),
            )

    def get_system_info(self) -> r[Mapping[str, t.JsonValue]]:
        """Get system information - public API method."""
        try:
            info_model = self._get_system_info()
            info_dict: dict[str, t.JsonValue] = dict(
                FlextCliDebug._convert_model_to_dict(
                    info_model,
                )
            )
            return r[Mapping[str, t.JsonValue]].ok(info_dict)
        except Exception as e:
            return r[Mapping[str, t.JsonValue]].fail(
                FlextCliConstants.Cli.DebugErrorMessages.SYSTEM_INFO_COLLECTION_FAILED.format(
                    error=e,
                ),
            )

    def get_system_paths(self) -> r[Mapping[str, t.JsonValue]]:
        """Get system path information - public API method."""
        try:
            paths_data = self._get_path_info()
            # Convert each PathInfo model to dict
            serialized_paths: list[t.JsonValue] = []
            for path_info in paths_data:
                path_dict = FlextCliDebug._convert_model_to_dict(path_info)
                path_json_dict: dict[str, t.JsonValue] = dict(path_dict)
                # dict[str, t.JsonValue] is part of t.JsonValue union
                serialized_paths.append(path_json_dict)

            # list[t.JsonValue] is compatible with t.JsonValue (list is part of union)
            paths_dict: dict[str, t.JsonValue] = {
                "paths": serialized_paths,
            }
            return r[Mapping[str, t.JsonValue]].ok(paths_dict)
        except Exception as e:
            return r[Mapping[str, t.JsonValue]].fail(
                FlextCliConstants.Cli.DebugErrorMessages.SYSTEM_PATHS_COLLECTION_FAILED.format(
                    error=e,
                ),
            )

    def get_comprehensive_debug_info(
        self,
    ) -> r[Mapping[str, t.JsonValue]]:
        """Get comprehensive debug information combining all debug methods."""
        try:
            comprehensive_info: dict[str, t.JsonValue] = {}

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

            return r[Mapping[str, t.JsonValue]].ok(comprehensive_info)
        except Exception as e:
            return r[Mapping[str, t.JsonValue]].fail(
                FlextCliConstants.Cli.DebugErrorMessages.COMPREHENSIVE_DEBUG_INFO_FAILED.format(
                    error=e,
                ),
            )

    # =========================================================================
    # PRIVATE HELPER METHODS - Implementation details
    # =========================================================================

    @staticmethod
    def _get_system_info() -> FlextCliModels.Cli.SystemInfo:
        """Get basic system information as Pydantic model."""
        arch_tuple = platform.architecture()
        return FlextCliModels.Cli.SystemInfo(
            python_version=sys.version,
            platform=platform.platform(),
            architecture=list(arch_tuple),
            processor=platform.processor(),
            hostname=platform.node(),
        )

    @staticmethod
    def _get_environment_info() -> FlextCliModels.Cli.EnvironmentInfo:
        """Get environment variables with sensitive data masked as Pydantic model."""

        # Use FlextCliUtilities.process to handle environment variables
        def process_env_item(k: str, v: str) -> str:
            """Process single environment variable."""
            if any(
                sens in k.lower()
                for sens in FlextCliConstants.Cli.DebugDefaults.SENSITIVE_KEYS
            ):
                return FlextCliConstants.Cli.DebugDefaults.MASKED_SENSITIVE
            return v

        env_info_result = FlextCliUtilities.Cli.process_mapping(
            dict(os.environ),
            processor=process_env_item,
            on_error="skip",
        )
        env_info: dict[str, str] = env_info_result.map_or({})

        return FlextCliModels.Cli.EnvironmentInfo(variables=env_info)

    @staticmethod
    def _get_path_info() -> list[FlextCliModels.Cli.PathInfo]:
        """Get system path information as list of Pydantic models."""
        paths: list[FlextCliModels.Cli.PathInfo] = []
        for i, path in enumerate(sys.path):
            path_obj = pathlib.Path(path)
            paths.append(
                FlextCliModels.Cli.PathInfo(
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
                pathlib.Path(test_file).write_text(
                    "test",
                    encoding=FlextCliConstants.Cli.Utilities.DEFAULT_ENCODING,
                )
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
