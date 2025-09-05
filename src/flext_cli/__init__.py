"""FLEXT CLI - CLI-specific functionality extending flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

CLI-specific functionality extending flext-core with command-line interface patterns,
authentication, configuration management, and CLI-specific utilities.

Architecture:
    Foundation: Constants, types, exceptions, protocols
    Core: Models, services, context, configuration
    Application: Commands, API functions, authentication, debug
    Infrastructure: Client, formatters, adapters, utilities
    Support: Decorators, helpers, output management

Key Components:
    FlextCliConfig: CLI configuration management with environment variables
    FlextCliContext: Execution context and session management
    FlextCliModels: CLI-specific domain models
    FlextCliServices: CLI service layer with health checks
    FlextCliApi: API client for CLI operations
    FlextCliAuth: Authentication and session management
    FlextCliFormatters: Output formatting and display utilities
    FlextCliDebug: Debug utilities and diagnostics

Examples:
    CLI configuration:
    >>> from flext_cli.config import FlextCliConfig
    >>> config = FlextCliConfig()
    >>> config.setup_cli()

    Authentication:
    >>> from flext_cli.auth import FlextCliAuth
    >>> auth = FlextCliAuth()
    >>> result = auth.login("username", "password")

    API operations:
    >>> from flext_cli.client import FlextApiClient
    >>> client = FlextApiClient()
    >>> response = client.get("/api/status")

Notes:
    - All CLI operations should use FlextResult[T] for error handling
    - Configuration is managed through FlextCliConfig
    - Authentication state is maintained in FlextCliContext
    - Follow Clean Architecture patterns with layered imports
    - Leverage flext-core foundation for common functionality
    - NO wildcard imports - use explicit imports from specific modules

"""

from __future__ import annotations

# =============================================================================
# VERSION INFORMATION
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
# CORE CLI CLASSES - Primary API surface
# =============================================================================

from flext_cli.api import FlextCliApi
from flext_cli.auth import FlextCliAuth, auth
from flext_cli.config import FlextCliConfig
from flext_cli.client import FlextApiClient
from flext_cli.core import FlextCliService
from flext_cli.context import FlextCliContext, FlextCliExecutionContext
from flext_cli.debug import FlextCliDebug, debug_cmd
from flext_cli.formatters import FlextCliFormatters
from flext_cli.models import FlextCliModels
from flext_cli.services import FlextCliServices

# =============================================================================
# UTILITY CLASSES
# =============================================================================

from flext_cli.constants import FlextCliConstants
from flext_cli.data_processing import FlextCliDataProcessing
from flext_cli.decorators import (
    FlextCliDecorators,
    flext_cli_require_confirmation,
    handle_service_result,
)
from flext_cli.domain_services import FlextCliDomainServices
from flext_cli.file_operations import FlextCliFileOperations
from flext_cli.interactions import FlextCliInteractions
from flext_cli.validation import FlextCliValidation

# =============================================================================
# COMMAND MODULES AND FUNCTIONS
# =============================================================================

from flext_cli.cmd import (
    FlextCliCmd,
    config,
    edit,
    get_cmd,
    path,
    set_value,
    show,
    validate,
)

# =============================================================================
# TYPE SYSTEM AND TYPE VARIABLES
# =============================================================================

from flext_cli.typings import (
    FlextTypes,
    E,
    F,
    P,
    R,
    T,
    U,
    V,
)

# =============================================================================
# EXCEPTIONS - Complete hierarchy
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
# CLI ENTRY POINT AND MAIN FUNCTIONS
# =============================================================================

from flext_cli.cli import FlextCliMain, cli, main

# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def get_cli_config() -> FlextCliConfig:
    """Get current CLI configuration instance.

    Returns:
        FlextCliConfig: Current configuration instance

    """
    return FlextCliConfig.get_current()


# =============================================================================
# EXPLICIT EXPORTS - NO AGGREGATION LOGIC
# =============================================================================

__all__ = [
    # =============================================================================
    # VERSION INFORMATION
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
    # CORE CLI CLASSES - Primary API surface
    # =============================================================================
    "FlextApiClient",
    "FlextCliApi",
    "FlextCliAuth",
    "FlextCliConfig",
    "FlextCliContext",
    "FlextCliDebug",
    "FlextCliExecutionContext",
    "FlextCliFormatters",
    "FlextCliModels",
    "FlextCliService",
    "FlextCliServices",
    # =============================================================================
    # UTILITY CLASSES
    # =============================================================================
    "FlextCliConstants",
    "FlextCliDataProcessing",
    "FlextCliDecorators",
    "FlextCliDomainServices",
    "FlextCliFileOperations",
    "FlextCliInteractions",
    "FlextCliValidation",
    # =============================================================================
    # COMMAND MODULES AND FUNCTIONS
    # =============================================================================
    "FlextCliCmd",
    "auth",
    "config",
    "debug_cmd",
    "edit",
    "flext_cli_require_confirmation",
    "handle_service_result",
    "get_cmd",
    "path",
    "set_value",
    "show",
    "validate",
    # =============================================================================
    # TYPE SYSTEM AND TYPE VARIABLES
    # =============================================================================
    "FlextTypes",
    "E",
    "F",
    "P",
    "R",
    "T",
    "U",
    "V",
    # =============================================================================
    # EXCEPTIONS - Complete hierarchy
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
    # CLI ENTRY POINT AND MAIN FUNCTIONS
    # =============================================================================
    "FlextCliMain",
    "cli",
    "main",
    # =============================================================================
    # CONVENIENCE FUNCTIONS
    # =============================================================================
    "get_cli_config",
]
