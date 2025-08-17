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
from flext_cli.core import FlextCliService

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
from flext_cli.simple_api import create_cli_context, setup_cli


def _deprecation_warning(old_name: str, new_name: str) -> None:
    """Issue a deprecation warning for legacy imports."""
    warnings.warn(
        f"{old_name} is deprecated, use {new_name} instead",
        DeprecationWarning,
        stacklevel=3,
    )


# Legacy aliases for common CLI components - likely used names
def cli_service(*args: object, **kwargs: object) -> object:
    """Legacy alias for FlextCliService."""
    _deprecation_warning("CliService", "FlextCliService")
    if FlextCliService is None:
        msg = "FlextCliService not available"
        raise ImportError(msg)
    return FlextCliService(*args, **kwargs)


def cli_api(*args: object, **kwargs: object) -> object:
    """Legacy alias for FlextCliApi."""
    _deprecation_warning("CliAPI", "FlextCliApi")
    if FlextCliApi is None:
        msg = "FlextCliApi not available"
        raise ImportError(msg)
    return FlextCliApi(*args, **kwargs)


def cliservice(*args: object, **kwargs: object) -> object:
    """Legacy alias for FlextCliService (capitalized variant)."""
    _deprecation_warning("CLIService", "FlextCliService")
    if FlextCliService is None:
        msg = "FlextCliService not available"
        raise ImportError(msg)
    return FlextCliService(*args, **kwargs)


def setup_flext_cli(*args: object, **kwargs: object) -> object:
    """Legacy alias for setup_cli."""
    _deprecation_warning("setup_flext_cli", "setup_cli")
    if setup_cli is None:
        msg = "setup_cli not available"
        raise ImportError(msg)
    return setup_cli(*args, **kwargs)


def create_context(*args: object, **kwargs: object) -> object:
    """Legacy alias for create_cli_context."""
    _deprecation_warning("create_context", "create_cli_context")
    if create_cli_context is None:
        msg = "create_cli_context not available"
        raise ImportError(msg)
    return create_cli_context(*args, **kwargs)


# Legacy exception aliases (more concise names that were probably used)
def cli_error(*args: object, **kwargs: object) -> FlextCliError:
    """Legacy alias for FlextCliError."""
    _deprecation_warning("CliError", "FlextCliError")
    return FlextCliError(*args, **kwargs)


def cli_validation_error(*args: object, **kwargs: object) -> FlextCliValidationError:
    """Legacy alias for FlextCliValidationError."""
    _deprecation_warning("CliValidationError", "FlextCliValidationError")
    return FlextCliValidationError(*args, **kwargs)


def cli_configuration_error(
    *args: object,
    **kwargs: object,
) -> FlextCliConfigurationError:
    """Legacy alias for FlextCliConfigurationError."""
    _deprecation_warning("CliConfigurationError", "FlextCliConfigurationError")
    return FlextCliConfigurationError(*args, **kwargs)


def cli_connection_error(*args: object, **kwargs: object) -> FlextCliConnectionError:
    """Legacy alias for FlextCliConnectionError."""
    _deprecation_warning("CliConnectionError", "FlextCliConnectionError")
    return FlextCliConnectionError(*args, **kwargs)


def cli_processing_error(*args: object, **kwargs: object) -> FlextCliProcessingError:
    """Legacy alias for FlextCliProcessingError."""
    _deprecation_warning("CliProcessingError", "FlextCliProcessingError")
    return FlextCliProcessingError(*args, **kwargs)


def cli_authentication_error(
    *args: object,
    **kwargs: object,
) -> FlextCliAuthenticationError:
    """Legacy alias for FlextCliAuthenticationError."""
    _deprecation_warning("CliAuthenticationError", "FlextCliAuthenticationError")
    return FlextCliAuthenticationError(*args, **kwargs)


def cli_timeout_error(*args: object, **kwargs: object) -> FlextCliTimeoutError:
    """Legacy alias for FlextCliTimeoutError."""
    _deprecation_warning("CliTimeoutError", "FlextCliTimeoutError")
    return FlextCliTimeoutError(*args, **kwargs)


def cli_command_error(*args: object, **kwargs: object) -> FlextCliCommandError:
    """Legacy alias for FlextCliCommandError."""
    _deprecation_warning("CliCommandError", "FlextCliCommandError")
    return FlextCliCommandError(*args, **kwargs)


def cli_argument_error(*args: object, **kwargs: object) -> FlextCliArgumentError:
    """Legacy alias for FlextCliArgumentError."""
    _deprecation_warning("CliArgumentError", "FlextCliArgumentError")
    return FlextCliArgumentError(*args, **kwargs)


def cli_format_error(*args: object, **kwargs: object) -> FlextCliFormatError:
    """Legacy alias for FlextCliFormatError."""
    _deprecation_warning("CliFormatError", "FlextCliFormatError")
    return FlextCliFormatError(*args, **kwargs)


def cli_output_error(*args: object, **kwargs: object) -> FlextCliOutputError:
    """Legacy alias for FlextCliOutputError."""
    _deprecation_warning("CliOutputError", "FlextCliOutputError")
    return FlextCliOutputError(*args, **kwargs)


def cli_context_error(*args: object, **kwargs: object) -> FlextCliContextError:
    """Legacy alias for FlextCliContextError."""
    _deprecation_warning("CliContextError", "FlextCliContextError")
    return FlextCliContextError(*args, **kwargs)


# Alternative naming patterns that might have been used
def command_line_error(*args: object, **kwargs: object) -> FlextCliError:
    """Legacy alias for FlextCliError (command line variant)."""
    _deprecation_warning("CommandLineError", "FlextCliError")
    return FlextCliError(*args, **kwargs)


# Legacy function aliases for setup and configuration
def init_cli(*args: object, **kwargs: object) -> object:
    """Legacy alias for setup_cli."""
    _deprecation_warning("init_cli", "setup_cli")
    if setup_cli is None:
        msg = "setup_cli not available"
        raise ImportError(msg)
    return setup_cli(*args, **kwargs)


def configure_cli(*args: object, **kwargs: object) -> object:
    """Legacy alias for setup_cli."""
    _deprecation_warning("configure_cli", "setup_cli")
    if setup_cli is None:
        msg = "setup_cli not available"
        raise ImportError(msg)
    return setup_cli(*args, **kwargs)


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
