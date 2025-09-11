"""FLEXT CLI - Unified CLI module using flext-core directly.

Single responsibility module eliminating ALL loose functions and providing
clean API surface. Uses flext-core utilities directly with SOURCE OF TRUTH
principle for all CLI module organization and metadata.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime
from functools import wraps
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from collections.abc import Callable

from flext_core import (
    FlextContainer,
    FlextDomainService,
    FlextLogger,
    FlextResult,
    FlextTypes,
)

from flext_cli.__version__ import (
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
    __version__,
    __version_info__,
)
from flext_cli.api import FlextCliApi
from flext_cli.auth import FlextCliAuth
from flext_cli.factory import FlextCliFactory
from flext_cli.cli import (
    FlextCliMain,
    auth as auth_click_cmd,
    cli,
    debug as debug_cmd,
    login as login_cmd,
    logout as logout_cmd,
    main,
    status as status_cmd,
)
from flext_cli.client import FlextApiClient
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.context import FlextCliContext, FlextCliExecutionContext
from flext_cli.core import FlextCliService
from flext_cli.data_processing import FlextCliDataProcessing
from flext_cli.debug import FlextCliDebug
from flext_cli.decorators import FlextCliDecorators
from flext_cli.domain_services import FlextCliDomainServices
from flext_cli.exceptions import (
    FlextCliArgumentError,
    FlextCliAuthenticationError,
    FlextCliCommandError,
    FlextCliConfigurationError,
    FlextCliConnectionError,
    FlextCliContextError,
    FlextCliError,
    FlextCliException,
    FlextCliFormatError,
    FlextCliOutputError,
    FlextCliProcessingError,
    FlextCliTimeoutError,
    FlextCliValidationError,
)
from flext_cli.file_operations import FlextCliFileOperations
from flext_cli.formatters import FlextCliFormatters
from flext_cli.interactions import FlextCliInteractions
from flext_cli.logging_setup import FlextCliLoggingSetup
from flext_cli.models import FlextCliModels
from flext_cli.services import FlextCliServices
from flext_cli.typings import (
    E,
    F,
    P,
    R,
    T,
    U,
    V,
)


class FlextCliModule(FlextDomainService[str]):
    """Unified CLI module service.

    Single responsibility: CLI module coordination and API exposure.
    Uses flext-core utilities directly without wrapper layers.
    """

    class _ModuleInfo(TypedDict):
        """Module information structure."""

        name: str
        version: str
        author: str
        description: str

    class _OperationsCatalog(TypedDict):
        """Available operations catalog."""

        config_operations: list[str]
        auth_operations: list[str]
        format_operations: list[str]
        utility_operations: list[str]

    def __init__(self) -> None:
        """Initialize CLI module service."""
        super().__init__()
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)
        self._module_info = self._load_module_info()

    def _load_module_info(self) -> FlextCliModule._ModuleInfo:
        """Load module information from source of truth."""
        return {
            "name": "flext-cli",
            "version": __version__,
            "author": __author__,
            "description": __description__,
        }

    def get_logger(self) -> FlextLogger:
        """Get logger instance."""
        return self._logger

    def get_cli_config(self) -> FlextResult[FlextCliConfig]:
        """Get current CLI configuration."""
        try:
            config = FlextCliConfig()
            return FlextResult[FlextCliConfig].ok(config)
        except Exception as e:
            return FlextResult[FlextCliConfig].fail(f"Config retrieval failed: {e}")

    def save_auth_token(self, token: str) -> FlextResult[None]:
        """Save authentication token using FlextCliAuth."""
        auth_result = _factory.create_default_auth_service()
        if auth_result.is_failure:
            return FlextResult[None].fail(f"Failed to create auth service: {auth_result.error}")
        return auth_result.value.save_auth_token(token)

    def create_table(
        self,
        data: list[FlextTypes.Core.Dict],
        title: str | None = None,
    ) -> FlextResult[str]:
        """Create formatted table using FlextCliFormatters."""
        formatters = FlextCliFormatters()
        table_result = formatters.format_table(data, title=title)
        if table_result.is_success:
            return FlextResult[str].ok(str(table_result.value))
        return FlextResult[str].fail(
            table_result.error or "Table formatting failed"
        )

    def format_output(self, data: object, format_type: str) -> FlextResult[str]:
        """Format output data using FlextCliFormatters."""
        formatters = FlextCliFormatters()
        return formatters.format_data(data, format_type)

    def check_authentication(self) -> FlextResult[bool]:
        """Check authentication status using FlextCliAuth."""
        auth_result = _factory.create_default_auth_service()
        if auth_result.is_failure:
            return FlextResult[bool].fail(f"Failed to create auth service: {auth_result.error}")
        return auth_result.value.check_authentication_status()

    def measure_execution_time(
        self,
        operation_name: str,
    ) -> FlextResult[dict[str, object]]:
        """Measure execution time."""
        try:
            start_time = time.time()
            execution_info = {
                "operation": operation_name,
                "start_time": start_time,
                "timestamp": datetime.now(UTC).isoformat(),
                "measurement_id": str(uuid.uuid4()),
            }
            return FlextResult[dict[str, object]].ok(execution_info)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(
                f"Execution time measurement failed: {e}"
            )

    def get_available_operations(
        self,
    ) -> FlextResult[FlextCliModule._OperationsCatalog]:
        """Get available operations catalog."""
        try:
            operations: FlextCliModule._OperationsCatalog = {
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
            return FlextResult[FlextCliModule._OperationsCatalog].ok(operations)
        except Exception as e:
            return FlextResult[FlextCliModule._OperationsCatalog].fail(
                f"Operations catalog failed: {e}"
            )

    def execute(self) -> FlextResult[str]:
        """Execute CLI module service."""
        try:
            return FlextResult[str].ok(
                f"FlextCliModule v{self._module_info['version']} initialized successfully"
            )
        except Exception as e:
            return FlextResult[str].fail(f"CLI module execution failed: {e}")

    def execute_cli_operation(
        self,
        operation_name: str,
        *args: object,
        **kwargs: object,
    ) -> FlextResult[object]:
        """Execute specific CLI operation."""
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
        """Convenience API for common CLI operations."""

        def __init__(self, module_service: FlextCliModule) -> None:
            """Initialize convenience API with module service."""
            self._module = module_service

        def get_config(self) -> FlextResult[FlextCliConfig]:
            """Get CLI configuration."""
            return self._module.get_cli_config()

        def save_token(self, token: str) -> FlextResult[None]:
            """Save authentication token."""
            return self._module.save_auth_token(token)

        def create_data_table(
            self,
            data: list[FlextTypes.Core.Dict],
            title: str | None = None,
        ) -> FlextResult[str]:
            """Create formatted data table."""
            return self._module.create_table(data, title)

        def format_data(self, data: object, format_type: str) -> FlextResult[str]:
            """Format data with specified format type."""
            return self._module.format_output(data, format_type)

        def is_authenticated(self) -> FlextResult[bool]:
            """Check authentication status."""
            return self._module.check_authentication()

        def time_operation(self, operation_name: str) -> FlextResult[dict[str, object]]:
            """Measure operation execution time."""
            return self._module.measure_execution_time(operation_name)

    class DecoratorFactory:
        """Factory for CLI decorators."""

        def __init__(self, module_service: FlextCliModule) -> None:
            """Initialize decorator factory with module service."""
            self._module = module_service

        def require_authentication(
            self,
        ) -> Callable[[Callable[..., object]], Callable[..., object]]:
            """Create authentication requirement decorator."""
            def decorator(func: Callable[..., object]) -> Callable[..., object]:
                @wraps(func)
                def wrapper(*args: object, **kwargs: object) -> object:
                    auth_result = self._module.check_authentication()
                    if auth_result.is_failure or not auth_result.value:
                        auth_error_msg = "Authentication required for this operation"
                        raise ValueError(auth_error_msg)
                    return func(*args, **kwargs)

                return wrapper

            return decorator

        def measure_time(
            self,
        ) -> Callable[[Callable[..., object]], Callable[..., object]]:
            """Create execution time measurement decorator."""
            def decorator(func: Callable[..., object]) -> Callable[..., object]:
                @wraps(func)
                def wrapper(*args: object, **kwargs: object) -> object:
                    timing_result = self._module.measure_execution_time(func.__name__)
                    if timing_result.is_success:
                        timing_msg = f"Operation timing: {timing_result.value}"
                        logger = self._module.get_logger()
                        logger.debug(timing_msg)
                    return func(*args, **kwargs)

                return wrapper

            return decorator


# Global module instance for convenience operations
_cli_module = FlextCliModule()
_convenience_api = FlextCliModule.ConvenienceAPI(_cli_module)
_decorator_factory = FlextCliModule.DecoratorFactory(_cli_module)

# Factory for creating components with proper dependency injection
_factory = FlextCliFactory()


# Test compatibility aliases
auth = auth_click_cmd
status = status_cmd
login = login_cmd
logout = logout_cmd
FlextCliCmd = FlextCliConfig
handle_service_result = FlextCliDecorators.handle_service_result
config = FlextCliConfig


def get_cli_config() -> FlextCliConfig:
    """Get CLI config instance - test compatibility."""
    return FlextCliConfig()


__all__ = [
    "E",
    "F",
    "FlextApiClient",
    "FlextCliApi",
    "FlextCliArgumentError",
    "FlextCliAuth",
    "FlextCliAuthenticationError",
    "FlextCliCmd",
    "FlextCliCommandError",
    "FlextCliConfig",
    "FlextCliConfigurationError",
    "FlextCliConnectionError",
    "FlextCliConstants",
    "FlextCliContext",
    "FlextCliContextError",
    "FlextCliDataProcessing",
    "FlextCliDebug",
    "FlextCliDecorators",
    "FlextCliDomainServices",
    "FlextCliError",
    "FlextCliException",
    "FlextCliExecutionContext",
    "FlextCliFactory",
    "FlextCliFileOperations",
    "FlextCliFormatError",
    "FlextCliFormatters",
    "FlextCliInteractions",
    "FlextCliLoggingSetup",
    "FlextCliMain",
    "FlextCliModels",
    "FlextCliModule",
    "FlextCliOutputError",
    "FlextCliProcessingError",
    "FlextCliService",
    "FlextCliServices",
    "FlextCliTimeoutError",
    "FlextCliValidationError",
    "P",
    "R",
    "T",
    "U",
    "V",
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
    "__version__",
    "__version_info__",
    "auth",
    "cli",
    "config",
    "debug_cmd",
    "get_cli_config",
    "handle_service_result",
    "login",
    "logout",
    "main",
    "status",
]
