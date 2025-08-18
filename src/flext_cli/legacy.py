"""Legacy compatibility facade for flext-cli.

This module provides backward compatibility for APIs that may have been refactored
or renamed during the Pydantic modernization process. It follows the same pattern
as flext-core's legacy.py to ensure consistent facade patterns across the ecosystem.

All imports here should be considered deprecated and may issue warnings.
Modern code should import directly from the appropriate modules.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import warnings

from flext_cli.api import FlextCliApi
from flext_cli.config import CLIConfig

# Import modern implementations to re-export under legacy names
from flext_cli.exceptions import (
    FlextCliArgumentError,
    FlextCliAuthenticationError,
    FlextCliCommandError,
    FlextCliConfigurationError,
    FlextCliConnectionError,
    FlextCliContextError,
    FlextCliError,
    FlextCliFormatError,
    FlextCliOutputError,
    FlextCliProcessingError,
    FlextCliTimeoutError,
    FlextCliValidationError,
)
from flext_cli.simple_api import setup_cli


def _deprecation_warning(old_name: str, new_name: str) -> None:
    """Issue a deprecation warning for legacy imports."""
    warnings.warn(
        f"{old_name} is deprecated, use {new_name} instead",
        DeprecationWarning,
        stacklevel=3,
    )


# Legacy aliases for common CLI components - likely used names
def cli_service(*_args: object, **_kwargs: object) -> object:
    """Legacy alias for FlextCliService."""
    _deprecation_warning("CliService", "FlextCliService")

    # FlextCliService is abstract, return a mock implementation
    class MockCliService:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

    return MockCliService(*_args, **_kwargs)


def cli_api(*args: object, **_kwargs: object) -> object:
    """Legacy alias for FlextCliApi."""
    _deprecation_warning("CliAPI", "FlextCliApi")
    return FlextCliApi(*args, **_kwargs)


def cliservice(*_args: object, **_kwargs: object) -> object:
    """Legacy alias for FlextCliService (capitalized variant)."""
    _deprecation_warning("CLIService", "FlextCliService")

    # FlextCliService is abstract, return a mock implementation
    class MockCliService:
        def __init__(self, *args: object, **_kwargs: object) -> None:
            pass

    return MockCliService()


def setup_flext_cli(*_args: object, **_kwargs: object) -> object:
    """Legacy alias for setup_cli."""
    _deprecation_warning("setup_flext_cli", "setup_cli")
    try:
        # Ignore args/kwargs since CLIConfig has specific type requirements
        return setup_cli()
    except (ImportError, AttributeError) as e:
        msg = "setup_cli not available"
        raise ImportError(msg) from e


def create_context(*_args: object, **_kwargs: object) -> object:
    """Legacy alias for create_cli_context."""
    _deprecation_warning("create_context", "create_cli_context")
    try:
        # CLIConfig already imported at module level
        # Create with defaults since CLIConfig has specific type requirements
        return CLIConfig()
    except Exception as e:
        msg = "create_cli_context not available"
        raise ImportError(msg) from e


# Legacy exception aliases (more concise names that were probably used)
def cli_error(*args: object, **_kwargs: object) -> FlextCliError:
    """Legacy alias for FlextCliError."""
    _deprecation_warning("CliError", "FlextCliError")
    # Convert args to expected types
    message = str(args[0]) if args else "CLI error"
    return FlextCliError(message)


def cli_validation_error(*args: object, **_kwargs: object) -> FlextCliValidationError:
    """Legacy alias for FlextCliValidationError."""
    _deprecation_warning("CliValidationError", "FlextCliValidationError")
    message = str(args[0]) if args else "Validation error"
    return FlextCliValidationError(message)


def cli_configuration_error(
    *args: object,
    **_kwargs: object,
) -> FlextCliConfigurationError:
    """Legacy alias for FlextCliConfigurationError."""
    _deprecation_warning("CliConfigurationError", "FlextCliConfigurationError")
    message = str(args[0]) if args else "Configuration error"
    return FlextCliConfigurationError(message)


def cli_connection_error(*args: object, **_kwargs: object) -> FlextCliConnectionError:
    """Legacy alias for FlextCliConnectionError."""
    _deprecation_warning("CliConnectionError", "FlextCliConnectionError")
    message = str(args[0]) if args else "Connection error"
    return FlextCliConnectionError(message)


def cli_processing_error(*args: object, **_kwargs: object) -> FlextCliProcessingError:
    """Legacy alias for FlextCliProcessingError."""
    _deprecation_warning("CliProcessingError", "FlextCliProcessingError")
    message = str(args[0]) if args else "Processing error"
    return FlextCliProcessingError(message)


def cli_authentication_error(
    *args: object,
    **_kwargs: object,
) -> FlextCliAuthenticationError:
    """Legacy alias for FlextCliAuthenticationError."""
    _deprecation_warning("CliAuthenticationError", "FlextCliAuthenticationError")
    message = str(args[0]) if args else "Authentication error"
    return FlextCliAuthenticationError(message)


def cli_timeout_error(*args: object, **_kwargs: object) -> FlextCliTimeoutError:
    """Legacy alias for FlextCliTimeoutError."""
    _deprecation_warning("CliTimeoutError", "FlextCliTimeoutError")
    message = str(args[0]) if args else "Timeout error"
    return FlextCliTimeoutError(message)


def cli_command_error(*args: object, **_kwargs: object) -> FlextCliCommandError:
    """Legacy alias for FlextCliCommandError."""
    _deprecation_warning("CliCommandError", "FlextCliCommandError")
    message = str(args[0]) if args else "Command error"
    return FlextCliCommandError(message)


def cli_argument_error(*args: object, **_kwargs: object) -> FlextCliArgumentError:
    """Legacy alias for FlextCliArgumentError."""
    _deprecation_warning("CliArgumentError", "FlextCliArgumentError")
    message = str(args[0]) if args else "Argument error"
    return FlextCliArgumentError(message)


def cli_format_error(*args: object, **_kwargs: object) -> FlextCliFormatError:
    """Legacy alias for FlextCliFormatError."""
    _deprecation_warning("CliFormatError", "FlextCliFormatError")
    message = str(args[0]) if args else "Format error"
    return FlextCliFormatError(message)


def cli_output_error(*args: object, **_kwargs: object) -> FlextCliOutputError:
    """Legacy alias for FlextCliOutputError."""
    _deprecation_warning("CliOutputError", "FlextCliOutputError")
    message = str(args[0]) if args else "Output error"
    return FlextCliOutputError(message)


def cli_context_error(*args: object, **_kwargs: object) -> FlextCliContextError:
    """Legacy alias for FlextCliContextError."""
    _deprecation_warning("CliContextError", "FlextCliContextError")
    message = str(args[0]) if args else "Context error"
    return FlextCliContextError(message)


# Alternative naming patterns that might have been used
def command_line_error(*args: object, **_kwargs: object) -> FlextCliError:
    """Legacy alias for FlextCliError (command line variant)."""
    _deprecation_warning("CommandLineError", "FlextCliError")
    message = str(args[0]) if args else "Command line error"
    return FlextCliError(message)


# Legacy function aliases for setup and configuration
def init_cli(*_args: object, **_kwargs: object) -> object:
    """Legacy alias for setup_cli."""
    _deprecation_warning("init_cli", "setup_cli")
    try:
        # Ignore args/kwargs since CLIConfig has specific type requirements
        return setup_cli()
    except (ImportError, AttributeError) as e:
        msg = "setup_cli not available"
        raise ImportError(msg) from e


def configure_cli(*_args: object, **_kwargs: object) -> object:
    """Legacy alias for setup_cli."""
    _deprecation_warning("configure_cli", "setup_cli")
    try:
        # Ignore args/kwargs since CLIConfig has specific type requirements
        return setup_cli()
    except (ImportError, AttributeError) as e:
        msg = "setup_cli not available"
        raise ImportError(msg) from e


# Export legacy aliases for backward compatibility
__all__ = [
    "cli_api",
    "cli_argument_error",
    "cli_authentication_error",
    "cli_command_error",
    "cli_configuration_error",
    "cli_connection_error",
    "cli_context_error",
    "cli_error",
    "cli_format_error",
    "cli_output_error",
    "cli_processing_error",
    "cli_service",
    "cli_timeout_error",
    "cli_validation_error",
    "cliservice",
    "command_line_error",
    "configure_cli",
    "create_context",
    "init_cli",
    "setup_flext_cli",
]
