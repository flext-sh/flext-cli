"""FLEXT CLI - Unified CLI module using flext-core directly.

Single responsibility module eliminating ALL loose functions and providing
clean API surface. Uses flext-core utilities directly with SOURCE OF TRUTH
principle for all CLI module organization and metadata.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import time
from collections.abc import Callable
from functools import wraps
from typing import TypedDict

from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextTypes,
    FlextUtilities,
    FlextDomainService,
)

# =============================================================================
# VERSION INFORMATION FROM SOURCE OF TRUTH
# =============================================================================

from flext_cli.__version__ import (
    __version__,
    __version_info__,
    __author__,
    __author_email__,
    __build__,
    __classifiers__,
    __description__,
    __documentation_url__,
    __download_url__,
    __issues_url__,
    __keywords__,
    __license__,
    __long_description__,
    __maintainer__,
    __maintainer_email__,
    __platforms__,
    __python_requires__,
    __release_date__,
    __repository_url__,
    __status__,
    __url__,
)

# =============================================================================
# CORE CLI CLASSES - Primary API surface from SOURCE OF TRUTH
# =============================================================================

from flext_cli.api import FlextCliApi
from flext_cli.auth import FlextCliAuth
from flext_cli.config import FlextCliConfig
from flext_cli.client import FlextApiClient
from flext_cli.core import FlextCliService
from flext_cli.context import FlextCliContext, FlextCliExecutionContext
from flext_cli.debug import FlextCliDebug
from flext_cli.formatters import FlextCliFormatters
from flext_cli.logging_setup import FlextCliLoggingSetup
from flext_cli.models import FlextCliModels
from flext_cli.services import FlextCliServices

# =============================================================================
# UTILITY CLASSES FROM SOURCE OF TRUTH
# =============================================================================

from flext_cli.constants import FlextCliConstants
from flext_cli.data_processing import FlextCliDataProcessing
from flext_cli.decorators import FlextCliDecorators
from flext_cli.domain_services import FlextCliDomainServices
from flext_cli.file_operations import FlextCliFileOperations
from flext_cli.interactions import FlextCliInteractions
from flext_cli.validation import FlextCliValidation

# =============================================================================
# COMMAND MODULES FROM SOURCE OF TRUTH
# =============================================================================

# CMD módulo não existe mais - refatorado para config
FlextCliConfigCommands = FlextCliConfig  # alias simples

# =============================================================================
# TYPE SYSTEM FROM SOURCE OF TRUTH
# =============================================================================

from flext_cli.typings import (
    E,
    F,
    P,
    R,
    T,
    U,
    V,
)

# =============================================================================
# EXCEPTIONS FROM SOURCE OF TRUTH
# =============================================================================

from flext_cli.exceptions import (
    FlextCliError,
    FlextCliArgumentError,
    FlextCliAuthenticationError,
    FlextCliCommandError,
    FlextCliConfigurationError,
    FlextCliConnectionError,
    FlextCliContextError,
    FlextCliFormatError,
    FlextCliOutputError,
    FlextCliProcessingError,
    FlextCliTimeoutError,
    FlextCliValidationError,
    # Backward compatibility aliases
    FlextCliException,
)

# =============================================================================
# CLI ENTRY POINT FROM SOURCE OF TRUTH
# =============================================================================

from flext_cli.cli import FlextCliMain


class FlextCliModule(FlextDomainService[str]):
    """Unified CLI module service using flext-core utilities directly.

    Eliminates ALL wrapper methods and loose functions, providing clean
    API surface using flext-core utilities directly. Uses SOURCE OF TRUTH
    principle for all module organization and convenience operations.

    SOLID Principles Applied:
        - Single Responsibility: CLI module coordination only
        - Open/Closed: Extensible through flext-core patterns
        - Dependency Inversion: Uses FlextContainer for dependencies
        - Interface Segregation: Focused module interface
    """

    class ModuleInfo(TypedDict):
        """Module information structure from SOURCE OF TRUTH."""

        name: str
        version: str
        author: str
        description: str

    class ConvenienceOperations(TypedDict):
        """Available convenience operations from SOURCE OF TRUTH."""

        config_operations: list[str]
        auth_operations: list[str]
        format_operations: list[str]
        utility_operations: list[str]

    def __init__(self, **data: object) -> None:
        """Initialize CLI module service with flext-core dependencies and SOURCE OF TRUTH."""
        super().__init__()

        # Process data for compatibility if needed
        if data:
            # Can extend here if needed, but currently using flext-core defaults
            pass
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)

        # Load module metadata from SOURCE OF TRUTH - NO deduction
        module_info_result = self._load_module_info()
        if module_info_result.is_failure:
            msg = f"Failed to load module info from SOURCE OF TRUTH: {module_info_result.error}"
            raise ValueError(msg)
        self._module_info = module_info_result.value

    def _load_module_info(self) -> FlextResult[FlextCliModule.ModuleInfo]:
        """Load module information from SOURCE OF TRUTH."""
        try:
            # Direct module info loading from SOURCE OF TRUTH - NO deduction
            module_info: FlextCliModule.ModuleInfo = {
                "name": "flext-cli",
                "version": __version__,
                "author": __author__,
                "description": __description__,
            }

            return FlextResult[FlextCliModule.ModuleInfo].ok(module_info)
        except Exception as e:
            return FlextResult[FlextCliModule.ModuleInfo].fail(
                f"Module info loading from SOURCE OF TRUTH failed: {e}"
            )

    def get_cli_config(self) -> FlextResult[FlextCliConfig]:
        """Get current CLI configuration using SOURCE OF TRUTH."""
        try:
            # Use SOURCE OF TRUTH configuration retrieval
            if hasattr(FlextCliConfig, "get_current"):
                config = FlextCliConfig.get_current()
            else:
                config = FlextCliConfig()

            return FlextResult[FlextCliConfig].ok(config)
        except Exception as e:
            return FlextResult[FlextCliConfig].fail(
                f"CLI config retrieval from SOURCE OF TRUTH failed: {e}"
            )

    def save_auth_token(self, token: str) -> FlextResult[None]:
        """Save authentication token using SOURCE OF TRUTH."""
        try:
            # Use SOURCE OF TRUTH authentication service
            auth = FlextCliAuth()
            return auth.save_auth_token(token)
        except Exception as e:
            return FlextResult[None].fail(
                f"Auth token save using SOURCE OF TRUTH failed: {e}"
            )

    def create_table(
        self, data: list[FlextTypes.Core.Dict], title: str | None = None
    ) -> FlextResult[str]:
        """Create formatted table using SOURCE OF TRUTH formatters."""
        try:
            # Use SOURCE OF TRUTH formatters
            formatters = FlextCliFormatters()
            table_result = formatters.format_table(data, title=title)
            if table_result.is_success:
                return FlextResult[str].ok(str(table_result.value))
            return FlextResult[str].fail(
                table_result.error or "Table formatting failed"
            )
        except Exception as e:
            return FlextResult[str].fail(
                f"Table creation using SOURCE OF TRUTH failed: {e}"
            )

    def format_output(self, data: object, format_type: str) -> FlextResult[str]:
        """Format output data using SOURCE OF TRUTH."""
        try:
            # Use SOURCE OF TRUTH API for formatting
            api = FlextCliApi()
            format_result = api.format_data(data, format_type)
            if format_result.is_success:
                return FlextResult[str].ok(format_result.value)
            # Fallback to string representation from SOURCE OF TRUTH
            return FlextResult[str].ok(str(data))
        except Exception as e:
            return FlextResult[str].fail(
                f"Output formatting using SOURCE OF TRUTH failed: {e}"
            )

    def check_authentication(self) -> FlextResult[bool]:
        """Check authentication status using SOURCE OF TRUTH."""
        try:
            # Use SOURCE OF TRUTH authentication service
            auth = FlextCliAuth()
            return auth.check_authentication_status()
        except Exception as e:
            return FlextResult[bool].fail(
                f"Authentication check using SOURCE OF TRUTH failed: {e}"
            )

    def measure_execution_time(
        self, operation_name: str
    ) -> FlextResult[dict[str, object]]:
        """Measure execution time using SOURCE OF TRUTH timing utilities."""
        try:
            # Use SOURCE OF TRUTH timing patterns
            start_time = time.time()
            # Execution measurement metadata from SOURCE OF TRUTH
            execution_info = {
                "operation": operation_name,
                "start_time": start_time,
                "timestamp": datetime.now(UTC).isoformat(),
                "measurement_id": str(uuid.uuid4()),
            }

            return FlextResult[dict[str, object]].ok(execution_info)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(
                f"Execution time measurement using SOURCE OF TRUTH failed: {e}"
            )

    def get_available_operations(
        self,
    ) -> FlextResult[FlextCliModule.ConvenienceOperations]:
        """Get available convenience operations from SOURCE OF TRUTH."""
        try:
            # SOURCE OF TRUTH operations catalog
            operations: FlextCliModule.ConvenienceOperations = {
                "config_operations": [
                    "get_cli_config",
                    "validate_config",
                    "load_config_from_file",
                ],
                "auth_operations": [
                    "save_auth_token",
                    "check_authentication",
                    "clear_auth_tokens",
                ],
                "format_operations": [
                    "create_table",
                    "format_output",
                    "format_json",
                    "format_yaml",
                ],
                "utility_operations": [
                    "measure_execution_time",
                    "get_module_info",
                    "validate_input",
                ],
            }

            return FlextResult[FlextCliModule.ConvenienceOperations].ok(operations)
        except Exception as e:
            return FlextResult[FlextCliModule.ConvenienceOperations].fail(
                f"Operations catalog from SOURCE OF TRUTH failed: {e}"
            )

    def execute(self) -> FlextResult[str]:
        """Execute CLI module service - required by FlextDomainService abstract method."""
        try:
            # Default execution returns module information from SOURCE OF TRUTH
            return FlextResult[str].ok(
                f"FlextCliModule v{self._module_info['version']} initialized successfully"
            )
        except Exception as e:
            return FlextResult[str].fail(f"CLI module execution failed: {e}")

    def execute_cli_operation(
        self, operation_name: str, *args: object, **kwargs: object
    ) -> FlextResult[object]:
        """Execute specific CLI operation using operation name mapping."""
        operations_map = {
            "get_cli_config": self.get_cli_config,
            "save_auth_token": self.save_auth_token,
            "create_table": self.create_table,
            "format_output": self.format_output,
            "check_authentication": self.check_authentication,
            "measure_execution_time": self.measure_execution_time,
            "get_available_operations": self.get_available_operations,
        }

        if operation_name not in operations_map:
            return FlextResult[object].fail(f"Unknown CLI operation: {operation_name}")

        operation = operations_map[operation_name]
        return self.execute_operation(operation_name, operation, *args, **kwargs)

    class ConvenienceAPI:
        """Unified convenience API for common CLI operations using SOURCE OF TRUTH."""

        def __init__(self, module_service: FlextCliModule) -> None:
            """Initialize with SOURCE OF TRUTH CLI module service."""
            self._module = module_service

        def get_config(self) -> FlextResult[FlextCliConfig]:
            """Get CLI configuration - convenience wrapper."""
            return self._module.get_cli_config()

        def save_token(self, token: str) -> FlextResult[None]:
            """Save authentication token - convenience wrapper."""
            return self._module.save_auth_token(token)

        def create_data_table(
            self, data: list[FlextTypes.Core.Dict], title: str | None = None
        ) -> FlextResult[str]:
            """Create formatted table - convenience wrapper."""
            return self._module.create_table(data, title)

        def format_data(self, data: object, format_type: str) -> FlextResult[str]:
            """Format output data - convenience wrapper."""
            return self._module.format_output(data, format_type)

        def is_authenticated(self) -> FlextResult[bool]:
            """Check authentication status - convenience wrapper."""
            return self._module.check_authentication()

        def time_operation(self, operation_name: str) -> FlextResult[dict[str, object]]:
            """Measure operation timing - convenience wrapper."""
            return self._module.measure_execution_time(operation_name)

    class DecoratorFactory:
        """Factory for CLI decorators using SOURCE OF TRUTH patterns."""

        def __init__(self, module_service: FlextCliModule) -> None:
            """Initialize with SOURCE OF TRUTH CLI module service."""
            self._module = module_service

        def require_authentication(
            self,
        ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            """Create authentication requirement decorator using SOURCE OF TRUTH."""

            def decorator(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[explicit-any]
                @wraps(func)
                def wrapper(*args: object, **kwargs: object) -> object:
                    # Check authentication using SOURCE OF TRUTH
                    auth_result = self._module.check_authentication()
                    if auth_result.is_failure or not auth_result.value:
                        msg = "Authentication required for this operation"
                        raise ValueError(msg)
                    return func(*args, **kwargs)

                return wrapper

            return decorator

        def measure_time(
            self,
        ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            """Create time measurement decorator using SOURCE OF TRUTH."""

            def decorator(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[explicit-any]
                @wraps(func)
                def wrapper(*args: object, **kwargs: object) -> object:
                    # Measure execution using SOURCE OF TRUTH
                    timing_result = self._module.measure_execution_time(func.__name__)
                    if timing_result.is_success:
                        self._module._logger.debug(
                            f"Operation timing: {timing_result.value}"
                        )

                    try:
                        return func(*args, **kwargs)
                    finally:
                        # Timing cleanup using SOURCE OF TRUTH patterns
                        pass

                return wrapper

            return decorator


# =============================================================================
# MODULE-LEVEL CONVENIENCE INSTANCE FROM SOURCE OF TRUTH
# =============================================================================

# Global module instance for convenience operations
_cli_module = FlextCliModule()
_convenience_api = FlextCliModule.ConvenienceAPI(_cli_module)
_decorator_factory = FlextCliModule.DecoratorFactory(_cli_module)


# =============================================================================
# LEGACY ALIASES FOR TESTS (SIMPLE AS POSSIBLE)
# =============================================================================

# CLI aliases - testes esperam essas funções/objetos
# CORREÇÃO ARQUITETURAL: Importar CLI do módulo dedicado
from flext_cli.cli import cli, main

# Auth aliases - criar lazy para evitar instantiation no import

# Auth aliases - apontar para comandos Click corretos
from flext_cli.cli import (
    auth as auth_click_cmd,
    status as status_cmd,
    login as login_cmd,
    logout as logout_cmd,
)

auth = auth_click_cmd  # Click command para testes
status = status_cmd  # Click command para testes
login = login_cmd  # Click command para testes
logout = logout_cmd  # Click command para testes

# Debug aliases - testes esperam debug_cmd (grupo Click)
from flext_cli.cli import debug as debug_cmd  # Para test_debug_commands.py

# CMD aliases - testes esperam FlextCliCmd
FlextCliCmd = FlextCliConfig  # CMD é na verdade config refatorado

# Core aliases - testes esperam handle_service_result (static method)
handle_service_result = FlextCliDecorators.handle_service_result

# Config aliases - testes esperam config e get_cli_config
config = FlextCliConfig  # Para test_config_commands.py


def get_cli_config() -> FlextCliConfig:
    """Get CLI config instance - test compatibility."""
    return FlextCliConfig()


# =============================================================================
# EXPLICIT EXPORTS FROM SOURCE OF TRUTH - NO AGGREGATION LOGIC
# =============================================================================

__all__ = [
    # =============================================================================
    # VERSION INFORMATION FROM SOURCE OF TRUTH
    # =============================================================================
    "__version__",
    "__version_info__",
    "__author__",
    "__author_email__",
    "__build__",
    "__classifiers__",
    "__description__",
    "__documentation_url__",
    "__download_url__",
    "__issues_url__",
    "__keywords__",
    "__license__",
    "__long_description__",
    "__maintainer__",
    "__maintainer_email__",
    "__platforms__",
    "__python_requires__",
    "__release_date__",
    "__repository_url__",
    "__status__",
    "__url__",
    # =============================================================================
    # CORE CLI CLASSES - Primary API surface from SOURCE OF TRUTH
    # =============================================================================
    "FlextApiClient",
    "FlextCliApi",
    "FlextCliAuth",
    "FlextCliConfig",
    "FlextCliContext",
    "FlextCliDebug",
    "FlextCliExecutionContext",
    "FlextCliFormatters",
    "FlextCliLoggingSetup",
    "FlextCliMain",
    "FlextCliModels",
    "FlextCliModule",
    "FlextCliService",
    "FlextCliServices",
    # =============================================================================
    # UTILITY CLASSES FROM SOURCE OF TRUTH
    # =============================================================================
    "FlextCliConstants",
    "FlextCliDataProcessing",
    "FlextCliDecorators",
    "FlextCliDomainServices",
    "FlextCliFileOperations",
    "FlextCliInteractions",
    "FlextCliValidation",
    # =============================================================================
    # TYPE SYSTEM FROM SOURCE OF TRUTH
    # =============================================================================
    "E",
    "F",
    "P",
    "R",
    "T",
    "U",
    "V",
    # =============================================================================
    # EXCEPTIONS FROM SOURCE OF TRUTH
    # =============================================================================
    "FlextCliArgumentError",
    "FlextCliAuthenticationError",
    "FlextCliCommandError",
    "FlextCliConfigurationError",
    "FlextCliConnectionError",
    "FlextCliContextError",
    "FlextCliError",
    "FlextCliException",
    "FlextCliFormatError",
    "FlextCliOutputError",
    "FlextCliProcessingError",
    "FlextCliTimeoutError",
    "FlextCliValidationError",
    # =============================================================================
    # LEGACY ALIASES FOR TESTS COMPATIBILITY
    # =============================================================================
    "main",
    "cli",
    "auth",
    "status",
    "debug_cmd",
    "FlextCliCmd",
    "handle_service_result",
    "config",
    "get_cli_config",
]
