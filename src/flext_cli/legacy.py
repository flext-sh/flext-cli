"""Legacy compatibility facade for flext-cli.

This module provides backward compatibility for APIs that may have been refactored
or renamed during the Pydantic modernization process. It follows the same pattern
as flext-core's legacy.py to ensure consistent facade patterns across the ecosystem.

All imports here should be considered deprecated and may issue warnings.
Modern code should import directly from the appropriate modules.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import warnings
from typing import Any

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

# Import CLI components
try:
    from flext_cli.cli import cli, main
    from flext_cli.core import FlextCliService
    from flext_cli.api import FlextCliApi
    from flext_cli.simple_api import setup_cli, create_cli_context
except ImportError:
    # Handle missing modules gracefully for backward compatibility
    cli = main = FlextCliService = FlextCliApi = setup_cli = create_cli_context = None


def _deprecation_warning(old_name: str, new_name: str) -> None:
    """Issue a deprecation warning for legacy imports."""
    warnings.warn(
        f"{old_name} is deprecated, use {new_name} instead",
        DeprecationWarning,
        stacklevel=3,
    )


# Legacy aliases for common CLI components - likely used names
def CliService(*args: Any, **kwargs: Any) -> Any:
    """Legacy alias for FlextCliService."""
    _deprecation_warning("CliService", "FlextCliService")
    if FlextCliService is None:
        raise ImportError("FlextCliService not available")
    return FlextCliService(*args, **kwargs)


def CliAPI(*args: Any, **kwargs: Any) -> Any:
    """Legacy alias for FlextCliApi."""
    _deprecation_warning("CliAPI", "FlextCliApi")
    if FlextCliApi is None:
        raise ImportError("FlextCliApi not available")
    return FlextCliApi(*args, **kwargs)


def CLIService(*args: Any, **kwargs: Any) -> Any:
    """Legacy alias for FlextCliService (capitalized variant)."""
    _deprecation_warning("CLIService", "FlextCliService")
    if FlextCliService is None:
        raise ImportError("FlextCliService not available")
    return FlextCliService(*args, **kwargs)


def setup_flext_cli(*args: Any, **kwargs: Any) -> Any:
    """Legacy alias for setup_cli."""
    _deprecation_warning("setup_flext_cli", "setup_cli")
    if setup_cli is None:
        raise ImportError("setup_cli not available")
    return setup_cli(*args, **kwargs)


def create_context(*args: Any, **kwargs: Any) -> Any:
    """Legacy alias for create_cli_context."""
    _deprecation_warning("create_context", "create_cli_context")
    if create_cli_context is None:
        raise ImportError("create_cli_context not available")
    return create_cli_context(*args, **kwargs)


# Legacy exception aliases (more concise names that were probably used)
def CliError(*args: Any, **kwargs: Any) -> FlextCliError:
    """Legacy alias for FlextCliError."""
    _deprecation_warning("CliError", "FlextCliError")
    return FlextCliError(*args, **kwargs)


def CliValidationError(*args: Any, **kwargs: Any) -> FlextCliValidationError:
    """Legacy alias for FlextCliValidationError."""
    _deprecation_warning("CliValidationError", "FlextCliValidationError")
    return FlextCliValidationError(*args, **kwargs)


def CliConfigurationError(*args: Any, **kwargs: Any) -> FlextCliConfigurationError:
    """Legacy alias for FlextCliConfigurationError."""
    _deprecation_warning("CliConfigurationError", "FlextCliConfigurationError")
    return FlextCliConfigurationError(*args, **kwargs)


def CliConnectionError(*args: Any, **kwargs: Any) -> FlextCliConnectionError:
    """Legacy alias for FlextCliConnectionError."""
    _deprecation_warning("CliConnectionError", "FlextCliConnectionError")
    return FlextCliConnectionError(*args, **kwargs)


def CliProcessingError(*args: Any, **kwargs: Any) -> FlextCliProcessingError:
    """Legacy alias for FlextCliProcessingError."""
    _deprecation_warning("CliProcessingError", "FlextCliProcessingError")
    return FlextCliProcessingError(*args, **kwargs)


def CliAuthenticationError(*args: Any, **kwargs: Any) -> FlextCliAuthenticationError:
    """Legacy alias for FlextCliAuthenticationError."""
    _deprecation_warning("CliAuthenticationError", "FlextCliAuthenticationError")
    return FlextCliAuthenticationError(*args, **kwargs)


def CliTimeoutError(*args: Any, **kwargs: Any) -> FlextCliTimeoutError:
    """Legacy alias for FlextCliTimeoutError."""
    _deprecation_warning("CliTimeoutError", "FlextCliTimeoutError")
    return FlextCliTimeoutError(*args, **kwargs)


def CliCommandError(*args: Any, **kwargs: Any) -> FlextCliCommandError:
    """Legacy alias for FlextCliCommandError."""
    _deprecation_warning("CliCommandError", "FlextCliCommandError")
    return FlextCliCommandError(*args, **kwargs)


def CliArgumentError(*args: Any, **kwargs: Any) -> FlextCliArgumentError:
    """Legacy alias for FlextCliArgumentError."""
    _deprecation_warning("CliArgumentError", "FlextCliArgumentError")
    return FlextCliArgumentError(*args, **kwargs)


def CliFormatError(*args: Any, **kwargs: Any) -> FlextCliFormatError:
    """Legacy alias for FlextCliFormatError."""
    _deprecation_warning("CliFormatError", "FlextCliFormatError")
    return FlextCliFormatError(*args, **kwargs)


def CliOutputError(*args: Any, **kwargs: Any) -> FlextCliOutputError:
    """Legacy alias for FlextCliOutputError."""
    _deprecation_warning("CliOutputError", "FlextCliOutputError")
    return FlextCliOutputError(*args, **kwargs)


def CliContextError(*args: Any, **kwargs: Any) -> FlextCliContextError:
    """Legacy alias for FlextCliContextError."""
    _deprecation_warning("CliContextError", "FlextCliContextError")
    return FlextCliContextError(*args, **kwargs)


# Alternative naming patterns that might have been used
def CommandLineError(*args: Any, **kwargs: Any) -> FlextCliError:
    """Legacy alias for FlextCliError (command line variant)."""
    _deprecation_warning("CommandLineError", "FlextCliError")
    return FlextCliError(*args, **kwargs)


def CLIError(*args: Any, **kwargs: Any) -> FlextCliError:
    """Legacy alias for FlextCliError (uppercase variant)."""
    _deprecation_warning("CLIError", "FlextCliError")
    return FlextCliError(*args, **kwargs)


# Legacy function aliases for setup and configuration
def init_cli(*args: Any, **kwargs: Any) -> Any:
    """Legacy alias for setup_cli."""
    _deprecation_warning("init_cli", "setup_cli")
    if setup_cli is None:
        raise ImportError("setup_cli not available")
    return setup_cli(*args, **kwargs)


def configure_cli(*args: Any, **kwargs: Any) -> Any:
    """Legacy alias for setup_cli."""
    _deprecation_warning("configure_cli", "setup_cli")
    if setup_cli is None:
        raise ImportError("setup_cli not available")
    return setup_cli(*args, **kwargs)


# Export legacy aliases for backward compatibility
__all__ = [
    # Legacy service aliases
    "CliService",
    "CliAPI",
    "CLIService",
    
    # Legacy setup function aliases
    "setup_flext_cli",
    "create_context",
    "init_cli",
    "configure_cli",
    
    # Legacy exception aliases (concise forms)
    "CliError",
    "CliValidationError",
    "CliConfigurationError",
    "CliConnectionError",
    "CliProcessingError",
    "CliAuthenticationError",
    "CliTimeoutError",
    "CliCommandError",
    "CliArgumentError",
    "CliFormatError",
    "CliOutputError",
    "CliContextError",
    
    # Alternative naming patterns
    "CommandLineError",
    "CLIError",
]