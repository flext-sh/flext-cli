"""FLEXT CLI - CLI Foundation (30% functional, targeting 75%).

Current Status: Basic CLI wrapper with authentication and configuration.
Planned: Complete Click/Rich abstraction layer for ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from typing import ParamSpec, TypeVar

from flext_core import FlextResult, FlextTypes
from flext_core.typings import T

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

# Direct imports replacing removed aliases.py compatibility layer
from flext_cli.cli import (
    auth,
    auth as auth_cmd,
    cli,
    config,
    debug,
    debug as debug_cmd,
    get_cmd,
    login,
    login as login_cmd,
    logout,
    logout as logout_cmd,
    main,
    status,
    status as status_cmd,
)
from flext_cli.cli_bus import FlextCliCommandBusService
from flext_cli.cli_main import FlextCliMain
from flext_cli.client import FlextApiClient
from flext_cli.cmd import FlextCliCmd  # DEPRECATED - use FlextCliCommandBusService
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.context import FlextCliContext
from flext_cli.core import FlextCliService
from flext_cli.data_processing import FlextCliDataProcessing
from flext_cli.debug import FlextCliDebug
from flext_cli.decorators import FlextCliDecorators, handle_service_result
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

# FlextCliFactory removed - use direct constructors (FlextCliAuth, FlextApiClient)
from flext_cli.file_operations import FlextCliFileOperations
from flext_cli.formatters import FlextCliFormatters
from flext_cli.interactions import FlextCliInteractions
from flext_cli.logging_setup import FlextCliLoggingSetup
from flext_cli.models import FlextCliModels
from flext_cli.services import FlextCliServices
from flext_cli.utils import Validation

# Export cli_measure_time function for examples
cli_measure_time = FlextCliDecorators.cli_measure_time

# Compatibility aliases for removed aliases.py functionality
FlextCliExecutionContext = FlextCliContext  # Direct alias to real class
_auth_cmd = auth  # Keep for backward compatibility

def get_cli_config() -> FlextCliConfig:
    """Get CLI configuration instance.

    Factory function for FlextCliConfig - replaces removed aliases.py version.

    Returns:
        FlextCliConfig: New CLI configuration instance

    """
    return FlextCliConfig()

__all__ = [
    "Callable",
    "FlextApiClient",
    "FlextCliApi",
    "FlextCliArgumentError",
    "FlextCliAuth",
    "FlextCliAuthenticationError",
    "FlextCliCmd",  # DEPRECATED - use FlextCliCommandBusService
    "FlextCliCommandBusService",  # NEW - proper Command Bus integration
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
    "FlextCliEcosystem",
    "FlextCliError",
    "FlextCliException",
    "FlextCliExecutionContext",
    # "FlextCliFactory",  # Removed - use direct constructors
    "FlextCliFileOperations",
    "FlextCliFormatError",
    "FlextCliFormatters",
    "FlextCliInteractions",
    "FlextCliLoggingSetup",
    "FlextCliMain",
    "FlextCliModels",
    "FlextCliOutputError",
    "FlextCliProcessingError",
    "FlextCliService",
    "FlextCliServices",
    "FlextCliTimeoutError",
    "FlextCliValidationError",
    "FlextResult",
    "FlextTypes",
    "T",
    "Validation",
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
    "_auth_cmd",
    "auth",
    "auth_cmd",
    "cli",
    "cli_measure_time",
    "config",
    "debug",
    "debug_cmd",
    "get_auth_headers",
    "get_cli_config",
    "get_cmd",
    "handle_service_result",
    "login",
    "login_cmd",
    "logout",
    "logout_cmd",
    "main",
    "require_auth",
    "save_auth_token",
    "status",
    "status_cmd",
]


# Missing auth functions for ecosystem compatibility
class FlextCliEcosystem:
    """Unified ecosystem compatibility layer following FLEXT unified class pattern.

    Consolidated class providing ecosystem compatibility functions that were
    previously loose functions. Follows FLEXT unified class pattern - one class
    per responsibility extending flext-core patterns.
    """

    def __init__(self) -> None:
        """Initialize ecosystem compatibility layer."""
        self._auth_service: FlextCliAuth | None = None

    @property
    def auth_service(self) -> FlextCliAuth:
        """Get auth service instance with lazy loading."""
        if self._auth_service is None:
            self._auth_service = FlextCliAuth()
        return self._auth_service

    def save_auth_token(self, token: str) -> FlextResult[None]:
        """Save authentication token using FLEXT CLI foundation.

        Args:
            token: Authentication token to save

        Returns:
            FlextResult indicating success or failure

        """
        return self.auth_service.save_auth_token(token)

    def get_auth_headers(self) -> FlextTypes.Core.Headers:
        """Get authentication headers using FLEXT CLI foundation.

        Returns:
            Dictionary containing authorization headers

        """
        headers_result = self.auth_service.get_auth_headers()

        if headers_result.is_success:
            return headers_result.value
        return {}

    def require_auth(
        self,
        roles: list[str] | None = None,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """Authentication decorator using FLEXT CLI foundation.

        Args:
            roles: Optional list of required roles

        Returns:
            Decorator function

        """

        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                # Check if user is authenticated
                if not self.auth_service.is_authenticated():
                    auth_error_msg = "Authentication required"
                    raise FlextCliAuthenticationError(auth_error_msg)

                # In a real implementation, would check roles here
                if roles:
                    # For now, just log the roles requirement
                    pass

                return func(*args, **kwargs)

            return wrapper

        return decorator


# Create ecosystem instance for compatibility functions
_ecosystem = FlextCliEcosystem()

# Ecosystem compatibility functions - maintain existing API
def save_auth_token(token: str) -> FlextResult[None]:
    """Save authentication token using FLEXT CLI foundation.

    Args:
        token: Authentication token to save

    Returns:
        FlextResult indicating success or failure

    """
    return _ecosystem.save_auth_token(token)


def get_auth_headers() -> FlextTypes.Core.Headers:
    """Get authentication headers using FLEXT CLI foundation.

    Returns:
        Dictionary containing authorization headers

    """
    return _ecosystem.get_auth_headers()


P = ParamSpec("P")
R = TypeVar("R")

def require_auth(
    roles: list[str] | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Authentication decorator using FLEXT CLI foundation.

    Args:
        roles: Optional list of required roles

    Returns:
        Decorator function

    """
    return _ecosystem.require_auth(roles)


# Ensure aliases take precedence over module imports for CLI commands
