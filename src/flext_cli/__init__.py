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

from flext_cli.__version__ import __version__, __version_info__

# =============================================================================
# CORE CLI CLASSES - Primary API surface
# =============================================================================

from flext_cli.api import FlextCliApi
from flext_cli.auth import FlextCliAuth
from flext_cli.config import FlextCliConfig
from flext_cli.client import FlextApiClient
from flext_cli.core import FlextCliService
from flext_cli.context import FlextCliContext
from flext_cli.debug import FlextCliDebug
from flext_cli.formatters import FlextCliFormatters
from flext_cli.models import FlextCliModels
from flext_cli.services import FlextCliServices

# =============================================================================
# UTILITY CLASSES
# =============================================================================

from flext_cli.constants import FlextCliConstants
from flext_cli.data_processing import FlextCliDataProcessing
from flext_cli.decorators import FlextCliDecorators
from flext_cli.domain_services import FlextCliDomainServices
from flext_cli.file_operations import FlextCliFileOperations
from flext_cli.interactions import FlextCliInteractions
from flext_cli.validation import FlextCliValidation

# =============================================================================
# TYPE SYSTEM AND PROTOCOLS
# =============================================================================

from flext_cli.typings import FlextCliTypes
from flext_cli.protocols import (
    create_flext_cli_data_processor,
    create_flext_cli_formatter,
    create_flext_cli_manager,
    flext_cli_export_data,
    flext_cli_format_data,
)

# =============================================================================
# EXCEPTIONS
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
)

# =============================================================================
# CLI ENTRY POINT
# =============================================================================

from flext_cli.cli import main

# =============================================================================
# EXPLICIT EXPORTS - NO AGGREGATION LOGIC
# =============================================================================

__all__ = [
    # Version information
    "__version__",
    "__version_info__",

    # Core CLI classes
    "FlextApiClient",
    "FlextCliApi",
    "FlextCliAuth",
    "FlextCliConfig",
    "FlextCliContext",
    "FlextCliDebug",
    "FlextCliFormatters",
    "FlextCliModels",
    "FlextCliService",
    "FlextCliServices",

    # Utility classes
    "FlextCliConstants",
    "FlextCliDataProcessing",
    "FlextCliDecorators",
    "FlextCliDomainServices",
    "FlextCliFileOperations",
    "FlextCliInteractions",
    "FlextCliValidation",

    # Type system and protocols
    "FlextCliTypes",
    "create_flext_cli_data_processor",
    "create_flext_cli_formatter",
    "create_flext_cli_manager",
    "flext_cli_export_data",
    "flext_cli_format_data",

    # Exceptions
    "FlextCliArgumentError",
    "FlextCliAuthenticationError",
    "FlextCliCommandError",
    "FlextCliConfigurationError",
    "FlextCliConnectionError",
    "FlextCliContextError",
    "FlextCliError",
    "FlextCliFormatError",
    "FlextCliOutputError",
    "FlextCliProcessingError",
    "FlextCliTimeoutError",
    "FlextCliValidationError",

    # CLI entry point
    "main",
]
